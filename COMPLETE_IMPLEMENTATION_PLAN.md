# NER10 Complete Implementation Plan
**Version**: 3.0 - COMPREHENSIVE
**Date**: 2025-11-24
**Scope**: ALL Gaps (GAP-01 to GAP-05) + ALL Improvements (IMP-01 to IMP-06)

---

## Overview

This plan implements a complete, production-grade NER10 system addressing:
- **5 Critical Gaps** from PROJECT_AUDIT.md
- **6 Improvements** from ICE_Improvements.md
- **4-Agent Neural Swarm** with rigorous QA gates
- **Comprehensive feedback loops** at every stage

**Total Duration**: 16 weeks
**Team**: 3-5 people (ML Engineer, DevOps, Annotator, QA, Research Engineer)

---

## Phase 0: Foundation (Weeks 1-2) - CORE INFRASTRUCTURE

### Week 1: Logging, Metrics, and Unit Tests

#### CORE-01: Structured Logging (COMPLETE ✅)
**Owner**: DATA_OPS
**Status**: Done (4,729 entities tracked)
**Deliverables**:
- ✅ `logs/ingestion.log` with Python logging
- ✅ `metrics/ingestion_metrics.json` with JSON metrics
- ✅ Tracking: files_processed, entities_extracted, errors, processing_time

#### CORE-02: Unit Tests for Ingestion (GAP-04 Partial)
**Owner**: DATA_OPS + QA_OFFICER
**Duration**: 2 days
**ICE Score**: 630 (Impact: 7, Confidence: 10, Ease: 9)

**Tasks**:
1. Create `tests/` directory structure
2. Install pytest: `pip install pytest pytest-cov`
3. Write test suite for `ingest_tags.py`:

```python
# tests/test_ingest_tags.py
import pytest
from scripts.ingest_tags import parse_file, extract_xml_tags, extract_wiki_tags

class TestXMLTagExtraction:
    def test_simple_xml_tag(self):
        text = "The <THREAT_ACTOR>APT29</THREAT_ACTOR> targeted systems."
        entities = extract_xml_tags(text)
        assert len(entities) == 1
        assert entities[0] == ("APT29", "THREAT_ACTOR", 4, 9)
    
    def test_whitespace_handling(self):
        text = "<EQUIPMENT>  Siemens S7-1200  </EQUIPMENT>"
        entities = extract_xml_tags(text)
        assert entities[0][0] == "Siemens S7-1200"  # Trimmed
    
    def test_nested_tags(self):
        text = "<SECTOR>Water <EQUIPMENT>SCADA</EQUIPMENT></SECTOR>"
        entities = extract_xml_tags(text)
        # Should extract both, not nested
        assert len(entities) == 2
    
    def test_malformed_tag(self):
        text = "<THREAT_ACTOR>APT29"  # Missing closing tag
        entities = extract_xml_tags(text)
        assert len(entities) == 0  # Should skip malformed

class TestWikiTagExtraction:
    def test_simple_wiki_tag(self):
        text = "The [[VULNERABILITY:CVE-2021-44228]] was exploited."
        entities = extract_wiki_tags(text)
        assert len(entities) == 1
        assert entities[0] == ("CVE-2021-44228", "VULNERABILITY", 4, 24)
    
    def test_multiple_wiki_tags(self):
        text = "[[THREAT_ACTOR:APT29]] used [[MALWARE:Cobalt Strike]]"
        entities = extract_wiki_tags(text)
        assert len(entities) == 2

class TestSchemaMapping:
    def test_valid_label_mapping(self):
        from scripts.ingest_tags import load_mapping
        mapping = load_mapping()
        assert "EQUIPMENT" in mapping['entities']
        assert len(mapping['entities']['EQUIPMENT']) > 0
    
    def test_unknown_label_handling(self):
        # Should map unknown labels to closest match or reject
        pass

# Run: pytest tests/ -v --cov=scripts
```

4. Write tests for `ingest_raw.py`:
```python
# tests/test_ingest_raw.py
def test_markdown_to_jsonl():
    # Test conversion of markdown to JSONL format
    pass

def test_file_filtering():
    # Test that only .md and .txt files are processed
    pass
```

5. Run tests and achieve 90%+ coverage

**Acceptance Criteria**:
- ✅ 30+ unit tests written
- ✅ Test coverage > 90% on ingestion scripts
- ✅ All tests pass
- ✅ CI/CD integration (GitHub Actions)

**Feedback Loop**:
- If tests fail → Fix bugs → Re-test
- If coverage < 90% → Add tests for uncovered code

---

#### CORE-03: Error Detection Pipeline (GAP-01 Phase 1)
**Owner**: DATA_OPS
**Duration**: 5 days
**ICE Score**: 540 (Impact: 10, Confidence: 9, Ease: 6)

**Tasks**:
1. Create `scripts/error_detection.py`:

```python
# scripts/error_detection.py
import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

class ErrorDetector:
    def __init__(self, schema_mapping, neo4j_driver, f1_thresholds):
        self.schema = schema_mapping
        self.neo4j = neo4j_driver
        self.f1_thresholds = f1_thresholds
        self.errors = []
    
    def detect_low_confidence(self, predictions: List[Dict]) -> List[Dict]:
        """Mechanism 1: Flag predictions with confidence < 0.70"""
        low_conf = []
        for pred in predictions:
            if pred.get('confidence', 1.0) < 0.70:
                low_conf.append({
                    "type": "LOW_CONFIDENCE",
                    "prediction": pred,
                    "confidence": pred['confidence'],
                    "priority": 1 - pred['confidence']  # Lower conf = higher priority
                })
        logger.info(f"Detected {len(low_conf)} low-confidence predictions")
        return low_conf
    
    def detect_schema_violations(self, predictions: List[Dict]) -> List[Dict]:
        """Mechanism 2: Flag entities not in schema"""
        violations = []
        for pred in predictions:
            label = pred.get('label')
            if label not in self.schema['entities']:
                violations.append({
                    "type": "SCHEMA_VIOLATION",
                    "prediction": pred,
                    "reason": f"Label '{label}' not in schema",
                    "priority": 0.9
                })
        logger.info(f"Detected {len(violations)} schema violations")
        return violations
    
    def detect_f1_degradation(self, entity_type: str, current_f1: float) -> Dict:
        """Mechanism 3: Flag if F1 drops below threshold"""
        threshold = self.f1_thresholds.get(entity_type, 0.75)
        if current_f1 < threshold:
            return {
                "type": "F1_DEGRADATION",
                "entity_type": entity_type,
                "current_f1": current_f1,
                "threshold": threshold,
                "drop": threshold - current_f1,
                "priority": 1.0  # Critical
            }
        return None
    
    def detect_relationship_violations(self, predictions: List[Dict]) -> List[Dict]:
        """Mechanism 4: Flag invalid relationships"""
        violations = []
        # Check if entities can form valid Neo4j relationships
        for pred in predictions:
            if 'relationships' in pred:
                for rel in pred['relationships']:
                    if not self._is_valid_relationship(rel):
                        violations.append({
                            "type": "RELATIONSHIP_VIOLATION",
                            "prediction": pred,
                            "relationship": rel,
                            "reason": "Invalid relationship type or target",
                            "priority": 0.7
                        })
        logger.info(f"Detected {len(violations)} relationship violations")
        return violations
    
    def _is_valid_relationship(self, rel: Dict) -> bool:
        # Check against Neo4j schema
        rel_type = rel.get('type')
        source_label = rel.get('source_label')
        target_label = rel.get('target_label')
        
        # Query Neo4j schema for valid relationships
        # (simplified - actual implementation would query Neo4j)
        valid_rels = self.schema.get('relationships', [])
        return rel_type in valid_rels
    
    def run_all_detectors(self, predictions: List[Dict], f1_scores: Dict) -> List[Dict]:
        """Run all 4 detection mechanisms"""
        all_errors = []
        
        # Mechanism 1: Low confidence
        all_errors.extend(self.detect_low_confidence(predictions))
        
        # Mechanism 2: Schema violations
        all_errors.extend(self.detect_schema_violations(predictions))
        
        # Mechanism 3: F1 degradation
        for entity_type, f1 in f1_scores.items():
            error = self.detect_f1_degradation(entity_type, f1)
            if error:
                all_errors.append(error)
        
        # Mechanism 4: Relationship violations
        all_errors.extend(self.detect_relationship_violations(predictions))
        
        # Sort by priority (highest first)
        all_errors.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Total errors detected: {len(all_errors)}")
        return all_errors

# Usage
if __name__ == "__main__":
    detector = ErrorDetector(
        schema_mapping=load_schema(),
        neo4j_driver=get_neo4j_driver(),
        f1_thresholds={"EQUIPMENT": 0.80, "VULNERABILITY": 0.75, "THREAT_ACTOR": 0.78}
    )
    
    # Load predictions from model
    predictions = load_predictions("predictions.json")
    f1_scores = calculate_f1_scores(predictions, ground_truth)
    
    errors = detector.run_all_detectors(predictions, f1_scores)
    
    # Save to correction queue
    save_to_queue(errors, "corrections_queue.jsonl")
```

2. Test error detection:
```python
# tests/test_error_detection.py
def test_low_confidence_detection():
    detector = ErrorDetector(schema, neo4j, thresholds)
    preds = [
        {"text": "APT29", "label": "THREAT_ACTOR", "confidence": 0.95},
        {"text": "Unknown", "label": "EQUIPMENT", "confidence": 0.65}
    ]
    errors = detector.detect_low_confidence(preds)
    assert len(errors) == 1
    assert errors[0]['prediction']['text'] == "Unknown"

def test_schema_violation_detection():
    detector = ErrorDetector(schema, neo4j, thresholds)
    preds = [{"text": "Something", "label": "INVALID_LABEL"}]
    errors = detector.detect_schema_violations(preds)
    assert len(errors) == 1
```

3. Integrate with pipeline:
```python
# In main pipeline
predictions = model.predict(texts)
errors = detector.run_all_detectors(predictions, f1_scores)
if errors:
    save_to_correction_queue(errors)
```

**Acceptance Criteria**:
- ✅ All 4 detection mechanisms operational
- ✅ Detects 95%+ of actual errors (validated on test set)
- ✅ False positive rate < 10%
- ✅ Outputs to `corrections_queue.jsonl`

**Feedback Loop**:
- If false positive rate > 10% → Adjust thresholds → Re-test
- If missing errors → Add detection logic → Re-test

---

### Week 2: Correction Queue and Initial Feedback Loop

#### LOOP-01: Correction Queue System (GAP-01 Phase 2)
**Owner**: DATA_OPS
**Duration**: 4 days
**ICE Score**: 567 (Impact: 9, Confidence: 9, Ease: 7)

**Tasks**:
1. Create correction queue database:
```sql
-- corrections_queue.sql
CREATE TABLE IF NOT EXISTS corrections_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    predicted_entities JSON,
    error_type TEXT,
    priority REAL,
    status TEXT DEFAULT 'PENDING',  -- PENDING, TIER1_REVIEW, TIER2_REVIEW, RESOLVED, REJECTED
    tier1_reviewer TEXT,
    tier1_correction JSON,
    tier1_timestamp DATETIME,
    tier2_reviewer TEXT,
    tier2_validation JSON,
    tier2_timestamp DATETIME,
    consensus_resolution JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_priority ON corrections_queue(priority DESC, status);
CREATE INDEX idx_status ON corrections_queue(status);
```

2. Implement queue manager:
```python
# correction/queue_manager.py
import sqlite3
import json
from datetime import datetime

class CorrectionQueueManager:
    def __init__(self, db_path="corrections_queue.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        with open("corrections_queue.sql") as f:
            self.conn.executescript(f.read())
    
    def add_to_queue(self, item: Dict):
        """Add error to correction queue"""
        self.conn.execute("""
            INSERT INTO corrections_queue (text, predicted_entities, error_type, priority)
            VALUES (?, ?, ?, ?)
        """, (
            item['text'],
            json.dumps(item['predicted_entities']),
            item['error_type'],
            item['priority']
        ))
        self.conn.commit()
    
    def get_next_for_tier1(self) -> Dict:
        """Get highest priority PENDING item"""
        cursor = self.conn.execute("""
            SELECT * FROM corrections_queue
            WHERE status = 'PENDING'
            ORDER BY priority DESC
            LIMIT 1
        """)
        return self._row_to_dict(cursor.fetchone())
    
    def submit_tier1_correction(self, item_id: int, reviewer: str, correction: Dict):
        """Tier 1 reviewer submits correction"""
        self.conn.execute("""
            UPDATE corrections_queue
            SET status = 'TIER1_REVIEW',
                tier1_reviewer = ?,
                tier1_correction = ?,
                tier1_timestamp = ?
            WHERE id = ?
        """, (reviewer, json.dumps(correction), datetime.now(), item_id))
        self.conn.commit()
    
    def get_next_for_tier2(self) -> Dict:
        """Get item for Tier 2 validation (20% sampling)"""
        # Sample 20% of TIER1_REVIEW items
        cursor = self.conn.execute("""
            SELECT * FROM corrections_queue
            WHERE status = 'TIER1_REVIEW'
            ORDER BY RANDOM()
            LIMIT 1
        """)
        return self._row_to_dict(cursor.fetchone())
    
    def submit_tier2_validation(self, item_id: int, reviewer: str, validation: Dict):
        """Tier 2 reviewer validates Tier 1 correction"""
        agreement = validation.get('agrees_with_tier1', False)
        
        if agreement:
            status = 'RESOLVED'
        else:
            status = 'TIER2_REVIEW'  # Needs consensus
        
        self.conn.execute("""
            UPDATE corrections_queue
            SET status = ?,
                tier2_reviewer = ?,
                tier2_validation = ?,
                tier2_timestamp = ?
            WHERE id = ?
        """, (status, reviewer, json.dumps(validation), datetime.now(), item_id))
        self.conn.commit()
    
    def resolve_consensus(self, item_id: int, resolution: Dict):
        """Expert resolves Tier 1/2 disagreement"""
        self.conn.execute("""
            UPDATE corrections_queue
            SET status = 'RESOLVED',
                consensus_resolution = ?
            WHERE id = ?
        """, (json.dumps(resolution), item_id))
        self.conn.commit()
    
    def get_resolved_corrections(self, limit=100) -> List[Dict]:
        """Get resolved corrections for retraining"""
        cursor = self.conn.execute("""
            SELECT * FROM corrections_queue
            WHERE status = 'RESOLVED'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        cursor = self.conn.execute("""
            SELECT 
                status,
                COUNT(*) as count,
                AVG(priority) as avg_priority
            FROM corrections_queue
            GROUP BY status
        """)
        stats = {row[0]: {"count": row[1], "avg_priority": row[2]} for row in cursor.fetchall()}
        return stats
```

3. Create Prodigy review interface:
```python
# correction/prodigy_review.py
import prodigy
from prodigy.components.loaders import JSONL

@prodigy.recipe("ner10-tier1-review")
def tier1_review_recipe(dataset, source):
    """Tier 1 correction review interface"""
    
    def get_stream():
        queue = CorrectionQueueManager()
        while True:
            item = queue.get_next_for_tier1()
            if not item:
                break
            
            yield {
                "text": item['text'],
                "spans": item['predicted_entities'],
                "meta": {
                    "queue_id": item['id'],
                    "error_type": item['error_type'],
                    "priority": item['priority']
                }
            }
    
    def update_db(answers):
        queue = CorrectionQueueManager()
        for answer in answers:
            if answer['answer'] == 'accept':
                queue.submit_tier1_correction(
                    item_id=answer['meta']['queue_id'],
                    reviewer=answer.get('session_id', 'unknown'),
                    correction=answer['spans']
                )
    
    return {
        "dataset": dataset,
        "view_id": "ner_manual",
        "stream": get_stream(),
        "update": update_db
    }
```

**Acceptance Criteria**:
- ✅ Queue database operational
- ✅ Tier 1/2 review workflow functional
- ✅ Consensus resolution works
- ✅ Prodigy interface integrated
- ✅ Queue stats dashboard

**Feedback Loop**:
- Daily: Review queue stats → If queue > 100 items → Increase review capacity
- Weekly: Measure IAA (Inter-Annotator Agreement) → If < 0.85 → Provide training

---

#### LOOP-02: Automated Retraining Trigger (GAP-01 Phase 3)
**Owner**: DATA_OPS
**Duration**: 3 days
**ICE Score**: 432 (Impact: 9, Confidence: 8, Ease: 6)

**Tasks**:
1. Create retraining trigger system:
```python
# training/retrain_trigger.py
import schedule
import time
from datetime import datetime

class RetrainingTrigger:
    def __init__(self, queue_manager, model_trainer):
        self.queue = queue_manager
        self.trainer = model_trainer
        self.last_retrain = None
        self.f1_history = []
    
    def check_triggers(self) -> bool:
        """Check if any retraining trigger is met"""
        triggers_met = []
        
        # Trigger 1: Weekly scheduled (Monday 02:00 UTC)
        if self._is_weekly_schedule():
            triggers_met.append("WEEKLY_SCHEDULE")
        
        # Trigger 2: High correction rate (>100/week)
        corrections_this_week = self._get_corrections_count(days=7)
        if corrections_this_week > 100:
            triggers_met.append(f"HIGH_CORRECTION_RATE ({corrections_this_week})")
        
        # Trigger 3: F1 drop (>0.05)
        current_f1 = self._get_current_f1()
        if self.f1_history and (self.f1_history[-1] - current_f1) > 0.05:
            triggers_met.append(f"F1_DROP ({self.f1_history[-1]:.3f} -> {current_f1:.3f})")
        
        # Trigger 4: Critical error (F1 < 0.75)
        if current_f1 < 0.75:
            triggers_met.append(f"CRITICAL_F1 ({current_f1:.3f})")
        
        # Trigger 5: Manual override (check flag file)
        if Path("RETRAIN_NOW.flag").exists():
            triggers_met.append("MANUAL_OVERRIDE")
            Path("RETRAIN_NOW.flag").unlink()
        
        if triggers_met:
            logger.info(f"Retraining triggers met: {triggers_met}")
            return True
        return False
    
    def execute_retraining(self):
        """Execute automated retraining"""
        logger.info("Starting automated retraining...")
        
        # Get resolved corrections
        corrections = self.queue.get_resolved_corrections(limit=1000)
        logger.info(f"Retrieved {len(corrections)} corrections")
        
        # Prepare training data
        train_data = self._prepare_training_data(corrections)
        
        # Retrain model
        new_model = self.trainer.retrain(
            base_model="models/current",
            corrections=train_data,
            iterations=30
        )
        
        # Validate new model
        validation_results = self._validate_model(new_model)
        
        if validation_results['passes_gate']:
            logger.info("Validation passed, deploying new model")
            self._deploy_model(new_model)
            self.last_retrain = datetime.now()
        else:
            logger.warning(f"Validation failed: {validation_results['reason']}")
            self._rollback()
    
    def run_scheduler(self):
        """Run continuous scheduler"""
        schedule.every().monday.at("02:00").do(self.execute_retraining)
        schedule.every(1).hours.do(self.check_triggers)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
```

2. Test retraining triggers:
```python
# tests/test_retrain_trigger.py
def test_weekly_trigger():
    trigger = RetrainingTrigger(queue, trainer)
    # Mock datetime to Monday 02:00
    assert trigger._is_weekly_schedule() == True

def test_high_correction_rate_trigger():
    trigger = RetrainingTrigger(queue, trainer)
    # Add 150 corrections to queue
    assert trigger.check_triggers() == True
```

**Acceptance Criteria**:
- ✅ All 5 triggers operational
- ✅ Automated retraining executes correctly
- ✅ Scheduler runs continuously
- ✅ Logging captures all trigger events

**Feedback Loop**:
- After each retrain → Measure F1 improvement → If < +0.02 → Review correction quality
- If retraining fails → Alert team → Manual intervention

---

## Phase 1: Core Feedback Loop (Weeks 3-4)

### Week 3: Validation Loop and Deployment Gate

#### LOOP-03: Validation Loop + Deployment Gate (GAP-01 Phase 4)
**Owner**: QA_OFFICER
**Duration**: 3 days
**ICE Score**: 630 (Impact: 10, Confidence: 9, Ease: 7)

**Tasks**:
1. Create held-out test set (never used in training):
```python
# validation/create_test_set.py
def create_held_out_test_set():
    """Create test set from 20% of annotated data"""
    all_files = load_annotated_files()
    
    # Stratified split by entity type
    test_files = stratified_split(all_files, test_size=0.20, stratify_by='entity_types')
    
    # Save to separate directory
    save_test_set(test_files, "test_set/")
    
    # CRITICAL: Never use these files in training
    add_to_gitignore("test_set/")
    
    logger.info(f"Created held-out test set: {len(test_files)} files")
```

2. Implement deployment gate:
```python
# validation/deployment_gate.py
class DeploymentGate:
    def __init__(self, test_set_path, thresholds):
        self.test_set = load_test_set(test_set_path)
        self.thresholds = thresholds
    
    def validate_model(self, model_path) -> Dict:
        """Validate model against held-out test set"""
        model = load_model(model_path)
        
        # Run predictions on test set
        predictions = []
        ground_truth = []
        
        for example in self.test_set:
            pred = model.predict(example['text'])
            predictions.append(pred)
            ground_truth.append(example['entities'])
        
        # Calculate metrics
        metrics = calculate_metrics(predictions, ground_truth)
        
        # Check deployment gates
        gates = {
            "f1_gate": metrics['f1'] >= self.thresholds['f1'],  # >= 0.80
            "precision_gate": metrics['precision'] >= self.thresholds['precision'],  # >= 0.80
            "recall_gate": metrics['recall'] >= self.thresholds['recall'],  # >= 0.78
            "regression_gate": self._check_no_regression(metrics)
        }
        
        passes = all(gates.values())
        
        return {
            "passes_gate": passes,
            "metrics": metrics,
            "gates": gates,
            "recommendation": "DEPLOY" if passes else "REJECT"
        }
    
    def _check_no_regression(self, new_metrics) -> bool:
        """Ensure no entity type regressed"""
        old_metrics = load_previous_metrics()
        
        for entity_type in new_metrics['per_entity']:
            old_f1 = old_metrics['per_entity'].get(entity_type, {}).get('f1', 0)
            new_f1 = new_metrics['per_entity'][entity_type]['f1']
            
            if new_f1 < old_f1 - 0.03:  # Allow 3% tolerance
                logger.warning(f"Regression detected for {entity_type}: {old_f1:.3f} -> {new_f1:.3f}")
                return False
        
        return True
```

3. Integrate with retraining pipeline:
```python
# In retrain_trigger.py
def _validate_model(self, new_model):
    gate = DeploymentGate(
        test_set_path="test_set/",
        thresholds={"f1": 0.80, "precision": 0.80, "recall": 0.78}
    )
    
    validation_results = gate.validate_model(new_model)
    
    if not validation_results['passes_gate']:
        # Send alert
        send_alert(f"Model validation failed: {validation_results['gates']}")
    
    return validation_results
```

**Acceptance Criteria**:
- ✅ Held-out test set created (never used in training)
- ✅ Deployment gate checks all 4 criteria
- ✅ Regression detection works
- ✅ Failed validations trigger alerts

**Feedback Loop**:
- After each deployment → Monitor production F1 → If drops > 0.05 → Rollback
- Weekly → Review test set → Ensure still representative

---

### Week 4: Continuous Improvement Analytics

#### OPT-01: Continuous Improvement Analytics (GAP-01 Phase 5)
**Owner**: ARCHITECT + QA_OFFICER
**Duration**: 4 days
**ICE Score**: 384 (Impact: 8, Confidence: 8, Ease: 6)

**Tasks**:
1. Implement weak entity identification:
```python
# analytics/weak_entity_analyzer.py
class WeakEntityAnalyzer:
    def __init__(self, corrections_db, metrics_db):
        self.corrections = corrections_db
        self.metrics = metrics_db
    
    def identify_weak_entities(self) -> List[Dict]:
        """Identify entity types with low F1 or high correction rate"""
        weak_entities = []
        
        # Get F1 scores by entity type
        f1_scores = self.metrics.get_f1_by_entity_type()
        
        # Get correction rates by entity type
        correction_rates = self._calculate_correction_rates()
        
        for entity_type in f1_scores.keys():
            f1 = f1_scores[entity_type]
            correction_rate = correction_rates.get(entity_type, 0)
            
            # Weak if: F1 < 0.75 OR correction rate > 20%
            if f1 < 0.75 or correction_rate > 0.20:
                weak_entities.append({
                    "entity_type": entity_type,
                    "f1": f1,
                    "correction_rate": correction_rate,
                    "priority": self._calculate_priority(f1, correction_rate)
                })
        
        # Sort by priority
        weak_entities.sort(key=lambda x: x['priority'], reverse=True)
        
        return weak_entities
    
    def _calculate_correction_rates(self) -> Dict:
        """Calculate correction rate per entity type"""
        total_predictions = self.metrics.get_total_predictions_by_type()
        total_corrections = self.corrections.get_total_corrections_by_type()
        
        rates = {}
        for entity_type in total_predictions.keys():
            preds = total_predictions[entity_type]
            corrs = total_corrections.get(entity_type, 0)
            rates[entity_type] = corrs / preds if preds > 0 else 0
        
        return rates
    
    def _calculate_priority(self, f1, correction_rate) -> float:
        """Higher priority = more urgent to improve"""
        # Weight F1 gap more heavily
        f1_gap = max(0, 0.85 - f1)  # Target F1 = 0.85
        return (f1_gap * 0.7) + (correction_rate * 0.3)
```

2. Implement pattern learning from corrections:
```python
# analytics/pattern_learner.py
class CorrectionPatternLearner:
    def __init__(self, corrections_db):
        self.corrections = corrections_db
    
    def learn_patterns(self) -> List[Dict]:
        """Extract patterns from corrections"""
        corrections = self.corrections.get_all_resolved()
        
        patterns = []
        
        # Pattern 1: Common false positives
        false_positives = self._find_common_false_positives(corrections)
        patterns.append({
            "type": "FALSE_POSITIVE",
            "patterns": false_positives,
            "recommendation": "Add negative examples to training"
        })
        
        # Pattern 2: Common false negatives
        false_negatives = self._find_common_false_negatives(corrections)
        patterns.append({
            "type": "FALSE_NEGATIVE",
            "patterns": false_negatives,
            "recommendation": "Add more examples of these entities"
        })
        
        # Pattern 3: Boundary errors (wrong span)
        boundary_errors = self._find_boundary_errors(corrections)
        patterns.append({
            "type": "BOUNDARY_ERROR",
            "patterns": boundary_errors,
            "recommendation": "Improve tokenization or use character-level model"
        })
        
        return patterns
    
    def _find_common_false_positives(self, corrections) -> List[Dict]:
        """Find entities frequently marked as incorrect"""
        false_pos = {}
        
        for corr in corrections:
            original = corr['predicted_entities']
            corrected = corr['tier1_correction']
            
            # Find entities removed in correction
            removed = set(original) - set(corrected)
            
            for entity in removed:
                key = (entity['text'], entity['label'])
                false_pos[key] = false_pos.get(key, 0) + 1
        
        # Return top 20
        return sorted(false_pos.items(), key=lambda x: x[1], reverse=True)[:20]
```

3. Generate monthly recommendations:
```python
# analytics/recommendation_generator.py
def generate_monthly_recommendations():
    """Generate improvement recommendations"""
    analyzer = WeakEntityAnalyzer(corrections_db, metrics_db)
    learner = CorrectionPatternLearner(corrections_db)
    
    weak_entities = analyzer.identify_weak_entities()
    patterns = learner.learn_patterns()
    
    recommendations = {
        "date": datetime.now().isoformat(),
        "weak_entities": weak_entities,
        "patterns": patterns,
        "action_items": []
    }
    
    # Generate action items
    for weak in weak_entities[:5]:  # Top 5
        recommendations['action_items'].append({
            "priority": "HIGH",
            "entity_type": weak['entity_type'],
            "action": f"Annotate 100 more examples of {weak['entity_type']}",
            "expected_improvement": "+0.05 F1"
        })
    
    # Save report
    save_report(recommendations, f"reports/recommendations_{datetime.now().strftime('%Y%m')}.json")
    
    return recommendations
```

**Acceptance Criteria**:
- ✅ Weak entity identification works
- ✅ Pattern learning extracts insights
- ✅ Monthly recommendations generated
- ✅ Action items prioritized

**Feedback Loop**:
- Monthly → Review recommendations → Implement top 3 → Measure impact
- If recommendations don't improve F1 → Revise analysis logic

---

## Phase 2: Schema Enhancement (Weeks 5-6)

### Week 5: Psychometric Entity Subtypes

#### SCHEMA-02: Psychometric Entity Subtypes (GAP-02)
**Owner**: ARCHITECT + DATA_OPS
**Duration**: 5 days
**ICE Score**: 360 (Impact: 9, Confidence: 8, Ease: 5)

**Tasks**:
1. Expand schema mapping to include subtypes:
```json
// schema_mapping_v2.json
{
  "entities": {
    "COGNITIVE_BIAS": {
      "subtypes": [
        "NORMALCY_BIAS",
        "AVAILABILITY_BIAS",
        "CONFIRMATION_BIAS",
        "AUTHORITY_BIAS",
        "RECENCY_BIAS",
        "OPTIMISM_BIAS",
        "ANCHORING_BIAS"
      ],
      "neo4j_labels": ["CognitiveBias"]
    },
    "THREAT_PERCEPTION": {
      "subtypes": [
        "REAL_THREAT",
        "IMAGINARY_THREAT",
        "SYMBOLIC_THREAT"
      ],
      "neo4j_labels": ["ThreatPerception"]
    },
    "EMOTION": {
      "subtypes": [
        "ANXIETY",
        "PANIC",
        "DENIAL",
        "COMPLACENCY",
        "FRUSTRATION",
        "SHOCK"
      ],
      "neo4j_labels": ["Emotion"]
    },
    "ATTACKER_MOTIVATION": {
      "subtypes": [
        "MONEY",
        "IDEOLOGY",
        "COMPROMISE",
        "EGO"
      ],
      "neo4j_labels": ["AttackerMotivation"]
    },
    "DEFENSE_MECHANISM": {
      "subtypes": [
        "DENIAL",
        "PROJECTION",
        "RATIONALIZATION",
        "SUBLIMATION"
      ],
      "neo4j_labels": ["DefenseMechanism"]
    },
    "SECURITY_CULTURE": {
      "subtypes": [
        "MATURE",
        "DEVELOPING",
        "IMMATURE"
      ],
      "neo4j_labels": ["SecurityCulture"]
    },
    "HISTORICAL_PATTERN": {
      "subtypes": [
        "ORGANIZATIONAL_BEHAVIOR",
        "SECTOR_BEHAVIOR",
        "ATTACKER_BEHAVIOR"
      ],
      "neo4j_labels": ["HistoricalPattern"]
    },
    "FUTURE_THREAT_PREDICTION": {
      "subtypes": [
        "TECHNICAL",
        "BEHAVIORAL",
        "GEOPOLITICAL"
      ],
      "neo4j_labels": ["FutureThreat"]
    }
  }
}
```

2. Update training config for subtypes:
```cfg
# configs/train_config_v2.cfg
[nlp]
lang = "en"
pipeline = ["tok2vec","ner"]
batch_size = 128

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"

# Add all subtypes as labels
[initialize.components.ner]
labels = [
    "EQUIPMENT", "VULNERABILITY", "THREAT_ACTOR", "MALWARE",
    "ATTACK_PATTERN", "SECTOR", "ORGANIZATION", "LOCATION",
    "NORMALCY_BIAS", "AVAILABILITY_BIAS", "CONFIRMATION_BIAS",
    "AUTHORITY_BIAS", "RECENCY_BIAS", "OPTIMISM_BIAS", "ANCHORING_BIAS",
    "REAL_THREAT", "IMAGINARY_THREAT", "SYMBOLIC_THREAT",
    "ANXIETY", "PANIC", "DENIAL", "COMPLACENCY", "FRUSTRATION", "SHOCK",
    "MONEY", "IDEOLOGY", "COMPROMISE", "EGO",
    "DENIAL_DEFENSE", "PROJECTION", "RATIONALIZATION", "SUBLIMATION",
    "MATURE_CULTURE", "DEVELOPING_CULTURE", "IMMATURE_CULTURE",
    "ORG_BEHAVIOR", "SECTOR_BEHAVIOR", "ATTACKER_BEHAVIOR",
    "TECH_PREDICTION", "BEHAVIORAL_PREDICTION", "GEO_PREDICTION"
]
```

3. Annotate examples for each subtype (500+ per subtype):
```python
# annotation/annotate_subtypes.py
def annotate_psychometric_subtypes():
    """Annotate examples for psychometric subtypes"""
    
    # Load existing cognitive bias annotations
    bias_files = load_files("Training_Data_Check_to_see/Cognitive_Biases/")
    
    # For each file, identify subtype
    for file in bias_files:
        text = file.read_text()
        
        # Extract existing <COGNITIVE_BIAS> tags
        biases = extract_xml_tags(text, "COGNITIVE_BIAS")
        
        # Use LLM to classify subtype
        for bias in biases:
            subtype = classify_bias_subtype(bias['text'])
            
            # Update annotation with subtype
            update_annotation(file, bias, subtype)
    
    logger.info(f"Annotated {len(bias_files)} files with subtypes")
```

4. Fine-tune model with subtypes:
```bash
# Train with subtypes
python -m spacy train configs/train_config_v2.cfg \
    --output models/ner10_v2 \
    --paths.train corpus/train.spacy \
    --paths.dev corpus/dev.spacy \
    --gpu-id 0
```

**Acceptance Criteria**:
- ✅ Schema expanded to 40+ labels (8 types × subtypes)
- ✅ 500+ examples annotated per subtype
- ✅ Model trained with subtypes
- ✅ F1 > 0.75 on psychometric entities

**Feedback Loop**:
- After training → Evaluate per-subtype F1 → If < 0.70 → Annotate more examples
- Weekly → Review subtype distribution → Ensure balanced

---

### Week 6: Relationship Extraction and Neo4j Agent

#### SCHEMA-03: Relationship Extraction (GAP-03)
**Owner**: ARCHITECT
**Duration**: 4 days
**ICE Score**: 196 (Impact: 7, Confidence: 7, Ease: 4)

**Tasks**:
1. Implement basic relationship extraction:
```python
# extraction/relationship_extractor.py
from spacy.matcher import DependencyMatcher

class RelationshipExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        self.matcher = DependencyMatcher(nlp.vocab)
        self._add_patterns()
    
    def _add_patterns(self):
        # Pattern 1: THREAT_ACTOR -> TARGETS -> SECTOR
        # "APT29 targeted water utilities"
        pattern = [
            {"RIGHT_ID": "actor", "RIGHT_ATTRS": {"ENT_TYPE": "THREAT_ACTOR"}},
            {"LEFT_ID": "actor", "REL_OP": ">", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["target", "attack", "compromise"]}}},
            {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["SECTOR", "ORGANIZATION", "EQUIPMENT"]}}}
        ]
        self.matcher.add("TARGETS", [pattern])
        
        # Pattern 2: THREAT_ACTOR -> USES -> MALWARE
        # "APT29 used Cobalt Strike"
        pattern = [
            {"RIGHT_ID": "actor", "RIGHT_ATTRS": {"ENT_TYPE": "THREAT_ACTOR"}},
            {"LEFT_ID": "actor", "REL_OP": ">", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["use", "deploy", "leverage"]}}},
            {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "malware", "RIGHT_ATTRS": {"ENT_TYPE": "MALWARE"}}
        ]
        self.matcher.add("USES_MALWARE", [pattern])
        
        # Pattern 3: MALWARE -> EXPLOITS -> VULNERABILITY
        # "Cobalt Strike exploited CVE-2021-44228"
        pattern = [
            {"RIGHT_ID": "malware", "RIGHT_ATTRS": {"ENT_TYPE": "MALWARE"}},
            {"LEFT_ID": "malware", "REL_OP": ">", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["exploit", "leverage", "abuse"]}}},
            {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "vuln", "RIGHT_ATTRS": {"ENT_TYPE": "VULNERABILITY"}}
        ]
        self.matcher.add("EXPLOITS", [pattern])
        
        # Pattern 4: VULNERABILITY -> AFFECTS -> EQUIPMENT
        # "CVE-2021-44228 affects Siemens S7-1200"
        pattern = [
            {"RIGHT_ID": "vuln", "RIGHT_ATTRS": {"ENT_TYPE": "VULNERABILITY"}},
            {"LEFT_ID": "vuln", "REL_OP": ">", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["affect", "impact", "target"]}}},
            {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "equip", "RIGHT_ATTRS": {"ENT_TYPE": "EQUIPMENT"}}
        ]
        self.matcher.add("AFFECTS", [pattern])
        
        # Pattern 5: ATTACK_PATTERN -> USES_TTP -> MITRE_TECHNIQUE
        # "Spear phishing uses T1566"
        pattern = [
            {"RIGHT_ID": "pattern", "RIGHT_ATTRS": {"ENT_TYPE": "ATTACK_PATTERN"}},
            {"LEFT_ID": "pattern", "REL_OP": ">", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["use", "implement", "employ"]}}},
            {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "ttp", "RIGHT_ATTRS": {"TEXT": {"REGEX": "^T[0-9]{4}"}}}
        ]
        self.matcher.add("USES_TTP", [pattern])
    
    def extract_relationships(self, doc) -> List[Dict]:
        """Extract relationships from spaCy doc"""
        matches = self.matcher(doc)
        
        relationships = []
        for match_id, token_ids in matches:
            rel_type = self.nlp.vocab.strings[match_id]
            
            # Get matched tokens
            tokens = [doc[i] for i in token_ids]
            
            # Extract source and target entities
            source = self._get_entity(tokens[0])
            target = self._get_entity(tokens[-1])
            
            if source and target:
                relationships.append({
                    "type": rel_type,
                    "source": source,
                    "target": target,
                    "confidence": 0.85  # Rule-based = high confidence
                })
        
        return relationships
    
    def _get_entity(self, token):
        """Get entity from token"""
        for ent in token.doc.ents:
            if token.i >= ent.start and token.i < ent.end:
                return {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
        return None

# Usage
extractor = RelationshipExtractor(nlp)
doc = nlp("APT29 targeted water utilities using CVE-2021-44228")
relationships = extractor.extract_relationships(doc)
# Output: [{"type": "TARGETS", "source": {"text": "APT29", ...}, "target": {"text": "water utilities", ...}}]
```

2. Test relationship extraction:
```python
# tests/test_relationship_extraction.py
def test_targets_relationship():
    extractor = RelationshipExtractor(nlp)
    doc = nlp("APT29 targeted water utilities")
    rels = extractor.extract_relationships(doc)
    
    assert len(rels) == 1
    assert rels[0]['type'] == "TARGETS"
    assert rels[0]['source']['text'] == "APT29"
    assert rels[0]['target']['text'] == "water utilities"

def test_exploits_relationship():
    extractor = RelationshipExtractor(nlp)
    doc = nlp("Cobalt Strike exploited CVE-2021-44228")
    rels = extractor.extract_relationships(doc)
    
    assert len(rels) == 1
    assert rels[0]['type'] == "EXPLOITS"
```

**Acceptance Criteria**:
- ✅ 5 relationship types extracted
- ✅ Precision > 0.80 on test set
- ✅ Recall > 0.60 (rule-based has lower recall)
- ✅ Integrated with main pipeline

**Feedback Loop**:
- Weekly → Review extracted relationships → Add new patterns for common cases
- If precision < 0.80 → Refine patterns → Re-test

---

#### SCHEMA-01: Neo4j "Systems" Agent (IMP-03)
**Owner**: ARCHITECT
**Duration**: 3 days
**ICE Score**: 560 (Impact: 8, Confidence: 10, Ease: 7)

**Tasks**:
1. Implement Neo4j validation agent (already detailed in DETAILED_SWARM_PLAN.md Day 5)
2. Integrate with main pipeline
3. Test schema compliance (100% enforcement)

**Acceptance Criteria**:
- ✅ Schema violations rejected (0% false accepts)
- ✅ Existing entities validated against Neo4j
- ✅ Novel entities accepted if schema-compliant

---

## Phase 3: Neural Swarm (Weeks 7-10)

### Weeks 7-10: Neural Annotation Swarm (IMP-01, IMP-02, IMP-05)

**Refer to DETAILED_SWARM_PLAN.md for complete implementation**

**Summary**:
- **Week 7**: Agent prompt engineering, individual agent testing, QA calibration
- **Week 8**: Coordinator implementation, Research Agent web search (IMP-02), integration testing
- **Week 9**: Human Fallback Queue (IMP-05), end-to-end testing, performance optimization
- **Week 10**: Production deployment, monitoring dashboard, documentation

**Key Deliverables**:
- 4-Agent Neural Swarm operational
- QA confidence calibrated (≥ 0.85 threshold)
- Research Agent validates unknowns via web search
- Human Fallback Queue for low-confidence annotations
- 1,431 raw files annotated with 80%+ automation

---

## Phase 4: Optimization & Production (Weeks 11-12)

### Week 11: Monitoring Dashboard

#### OPT-02: Monitoring Dashboard (IMP-04 Enhancement)
**Owner**: PRAGMATIST + QA_OFFICER
**Duration**: 3 days
**ICE Score**: 441 (Impact: 7, Confidence: 9, Ease: 7)

**Tasks**:
1. Create Streamlit dashboard:
```python
# dashboard/monitoring_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="NER10 Monitoring Dashboard", layout="wide")

# Sidebar
st.sidebar.title("NER10 Monitoring")
time_range = st.sidebar.selectbox("Time Range", ["Last 24h", "Last 7d", "Last 30d", "All Time"])

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Overall F1 Score", "0.82", "+0.03")

with col2:
    st.metric("QA Confidence (Avg)", "0.87", "+0.02")

with col3:
    st.metric("Fallback Queue Size", "23", "-5")

with col4:
    st.metric("Annotations/Day", "156", "+12")

# F1 Score by Entity Type
st.subheader("F1 Score by Entity Type")
f1_data = load_f1_scores_by_type(time_range)
fig = px.bar(f1_data, x='entity_type', y='f1', color='f1',
             color_continuous_scale='RdYlGn', range_color=[0.5, 1.0])
st.plotly_chart(fig, use_container_width=True)

# Agent Performance
st.subheader("Neural Swarm Agent Performance")
agent_data = load_agent_performance(time_range)
fig = px.line(agent_data, x='date', y='confidence', color='agent',
              title="Agent Confidence Over Time")
st.plotly_chart(fig, use_container_width=True)

# Correction Queue Stats
st.subheader("Correction Queue Statistics")
queue_stats = load_queue_stats()
col1, col2 = st.columns(2)

with col1:
    st.write("Queue Status")
    st.dataframe(queue_stats['by_status'])

with col2:
    st.write("Top Priority Items")
    st.dataframe(queue_stats['top_priority'])

# IAA (Inter-Annotator Agreement)
st.subheader("Inter-Annotator Agreement")
iaa_data = load_iaa_metrics(time_range)
st.metric("Current IAA (Cohen's Kappa)", f"{iaa_data['current']:.3f}", 
          f"{iaa_data['change']:+.3f}")

# Recent Errors
st.subheader("Recent Errors Detected")
errors = load_recent_errors(limit=10)
st.dataframe(errors[['timestamp', 'error_type', 'entity_type', 'priority']])

# Run: streamlit run dashboard/monitoring_dashboard.py
```

2. Set up automated reporting:
```python
# reporting/weekly_report.py
def generate_weekly_report():
    """Generate weekly performance report"""
    report = {
        "week": datetime.now().strftime("%Y-W%W"),
        "metrics": {
            "overall_f1": calculate_overall_f1(),
            "qa_confidence_avg": calculate_avg_qa_confidence(),
            "annotations_completed": count_annotations_this_week(),
            "fallback_queue_size": get_queue_size(),
            "iaa": calculate_iaa()
        },
        "weak_entities": identify_weak_entities(),
        "top_errors": get_top_errors(limit=10),
        "recommendations": generate_recommendations()
    }
    
    # Send email report
    send_email_report(report, recipients=["team@example.com"])
    
    # Save to file
    save_report(report, f"reports/weekly_{report['week']}.json")
```

**Acceptance Criteria**:
- ✅ Dashboard displays real-time metrics
- ✅ Weekly reports automated
- ✅ Alerts configured for critical issues
- ✅ Accessible to all team members

---

### Week 12: Final Testing and Documentation

#### Production Readiness Checklist
**Owner**: ALL AGENTS

**Tasks**:
1. **Final End-to-End Testing** (100 files)
   - Smoke tests: 20 files (expected 100% accuracy)
   - Edge cases: 50 files (expected 80%+ accuracy)
   - Adversarial: 30 files (expected 90%+ rejection)

2. **Performance Benchmarking**
   - Throughput: > 100 files/hour
   - Latency: < 10s per file
   - Memory: < 8GB total

3. **Documentation**
   - User guide for annotators
   - API documentation
   - Troubleshooting guide
   - Deployment guide

4. **Deployment**
   - Deploy to production
   - Monitor for 48 hours
   - Collect feedback
   - Iterate

**Acceptance Criteria**:
- ✅ All tests pass
- ✅ Performance meets targets
- ✅ Documentation complete
- ✅ Production deployment successful

---

## Success Metrics Summary

### Phase 0 (Weeks 1-2)
- ✅ Structured logging operational (4,729 entities tracked)
- ✅ Unit tests: 90%+ coverage
- ✅ Error detection: 95%+ accuracy
- ✅ Correction queue: Tier 1/2 workflow functional

### Phase 1 (Weeks 3-4)
- ✅ Validation loop: F1 > 0.80 gate enforced
- ✅ Continuous improvement: Weak entities identified
- ✅ Automated retraining: 5 triggers operational

### Phase 2 (Weeks 5-6)
- ✅ Psychometric subtypes: 40+ labels, F1 > 0.75
- ✅ Relationship extraction: 5 types, Precision > 0.80
- ✅ Neo4j agent: 100% schema compliance

### Phase 3 (Weeks 7-10)
- ✅ Neural Swarm: 4 agents operational
- ✅ QA confidence: Calibrated (≥ 0.85 threshold)
- ✅ Research Agent: Validation accuracy > 0.85
- ✅ Human Fallback: Queue operational

### Phase 4 (Weeks 11-12)
- ✅ Monitoring dashboard: Real-time metrics
- ✅ Production deployment: F1 > 0.85
- ✅ Documentation: Complete

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Neural Swarm underperforms | 40% | High | Human Fallback Queue (IMP-05) |
| Training data insufficient | 50% | Medium | Neural Swarm accelerates annotation |
| F1 doesn't reach 0.85 | 30% | High | Continuous improvement loop identifies weak entities |
| Resource constraints | 60% | High | Phases 0-2 deliver value with 3 people |
| QA Officer overconfident | 40% | High | Calibration loop (Week 7 Day 3) |

---

## Next Steps

1. **Immediate** (This Week):
   - Complete CORE-02 (Unit Tests)
   - Begin CORE-03 (Error Detection)

2. **Short-term** (Weeks 3-4):
   - Implement full feedback loop
   - Deploy validation gate

3. **Medium-term** (Weeks 5-10):
   - Expand to psychometric subtypes
   - Build Neural Swarm

4. **Long-term** (Weeks 11-16):
   - Production deployment
   - Continuous monitoring and improvement

---

**END OF COMPLETE IMPLEMENTATION PLAN**

---

## APPENDIX A: Exact Next Prompts for Each Task

### How to Use This Appendix

Each task below has an **EXACT PROMPT** you can copy-paste to execute that specific task. The prompts are designed to:
1. Be self-contained (include all context)
2. Specify exact deliverables
3. Include testing requirements
4. Include git commit workflow
5. Trigger the appropriate agent persona

**Format**:
```
TASK: [Task Name]
AGENT: [Which agent should handle this]
PROMPT: [Exact prompt to copy-paste]
```

---

### CORE-02: Unit Tests for Ingestion

**TASK**: CORE-02 - Unit Tests for Ingestion  
**AGENT**: DATA_OPS + QA_OFFICER  
**DURATION**: 2 days  
**DEPENDENCIES**: CORE-01 (Complete ✅)

**EXACT PROMPT**:
```
Act as DATA_OPS. Implement CORE-02: Unit Tests for Ingestion.

CONTEXT:
- We have completed CORE-01 (structured logging)
- `scripts/ingest_tags.py` and `scripts/ingest_raw.py` exist
- We need 90%+ test coverage before proceeding to error detection

TASKS:
1. Create directory structure:
   - mkdir -p tests/
   - touch tests/__init__.py
   - touch tests/test_ingest_tags.py
   - touch tests/test_ingest_raw.py

2. Install pytest:
   - Activate venv: source venv/bin/activate
   - pip install pytest pytest-cov

3. Create tests/test_ingest_tags.py with these test classes:
   - TestXMLTagExtraction (4 tests: simple, whitespace, nested, malformed)
   - TestWikiTagExtraction (2 tests: simple, multiple)
   - TestSchemaMapping (2 tests: valid_label, unknown_label)
   
4. Create tests/test_ingest_raw.py with these tests:
   - test_markdown_to_jsonl
   - test_file_filtering
   
5. Run tests:
   - pytest tests/ -v --cov=scripts --cov-report=term-missing
   
6. Achieve 90%+ coverage. If not:
   - Identify uncovered lines
   - Add tests for uncovered code
   - Re-run pytest

7. Git workflow:
   - git add tests/
   - git commit -m "feat(testing): Add unit tests for ingestion (CORE-02)
   
   - Added 30+ unit tests for ingest_tags.py and ingest_raw.py
   - Achieved 90%+ test coverage
   - Tests cover: XML tags, Wiki tags, schema mapping, file filtering
   - All tests passing
   
   Closes: CORE-02"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ 30+ unit tests written
- ✅ Test coverage > 90%
- ✅ All tests pass
- ✅ Committed to git with proper message

OUTPUT:
- Show pytest output with coverage report
- Show git commit hash
- Confirm: "CORE-02 complete, ready for CORE-03"
```

**NEXT TASK AFTER COMPLETION**: CORE-03 (Error Detection Pipeline)

---

### CORE-03: Error Detection Pipeline

**TASK**: CORE-03 - Error Detection Pipeline  
**AGENT**: DATA_OPS  
**DURATION**: 5 days  
**DEPENDENCIES**: CORE-02 (Unit Tests)

**EXACT PROMPT**:
```
Act as DATA_OPS. Implement CORE-03: Error Detection Pipeline (GAP-01 Phase 1).

CONTEXT:
- CORE-01 and CORE-02 are complete
- We need 4 error detection mechanisms before building the correction queue
- This is the foundation of the feedback loop

TASKS:
1. Create scripts/error_detection.py with ErrorDetector class:
   - detect_low_confidence(predictions) -> flags confidence < 0.70
   - detect_schema_violations(predictions) -> flags invalid labels
   - detect_f1_degradation(entity_type, f1) -> flags F1 < threshold
   - detect_relationship_violations(predictions) -> flags invalid relationships
   - run_all_detectors(predictions, f1_scores) -> runs all 4 mechanisms

2. Create tests/test_error_detection.py with:
   - test_low_confidence_detection (2 predictions, 1 flagged)
   - test_schema_violation_detection (1 invalid label)
   - test_f1_degradation_detection (F1 drop scenario)
   - test_relationship_violation_detection (invalid relationship)
   - test_run_all_detectors (integration test)

3. Test with sample data:
   - Create sample_predictions.json with 10 predictions (mix of good/bad)
   - Run: python scripts/error_detection.py
   - Verify: errors saved to corrections_queue.jsonl

4. Validate accuracy:
   - Create test set of 100 predictions with known errors
   - Run error detection
   - Calculate: detection_rate = detected_errors / total_errors
   - Ensure: detection_rate > 0.95

5. Git workflow:
   - git add scripts/error_detection.py tests/test_error_detection.py
   - git commit -m "feat(feedback): Implement error detection pipeline (CORE-03)
   
   - Added 4 error detection mechanisms
   - Low confidence detection (threshold: 0.70)
   - Schema violation detection
   - F1 degradation monitoring
   - Relationship validation
   - Detection accuracy: 95%+
   - All tests passing
   
   Closes: CORE-03, Addresses: GAP-01 Phase 1"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ All 4 detection mechanisms operational
- ✅ Detection accuracy > 95% on test set
- ✅ False positive rate < 10%
- ✅ Outputs to corrections_queue.jsonl
- ✅ All tests pass

OUTPUT:
- Show detection results on sample data
- Show test output
- Show git commit hash
- Confirm: "CORE-03 complete, ready for LOOP-01"
```

**NEXT TASK AFTER COMPLETION**: LOOP-01 (Correction Queue System)

---

### LOOP-01: Correction Queue System

**TASK**: LOOP-01 - Correction Queue System  
**AGENT**: DATA_OPS  
**DURATION**: 4 days  
**DEPENDENCIES**: CORE-03 (Error Detection)

**EXACT PROMPT**:
```
Act as DATA_OPS. Implement LOOP-01: Correction Queue System (GAP-01 Phase 2).

CONTEXT:
- Error detection (CORE-03) is complete and flagging errors
- We need a database-backed queue for Tier 1/2 review workflow
- This enables human-in-the-loop corrections

TASKS:
1. Create correction/corrections_queue.sql:
   - Define corrections_queue table with all fields
   - Add indexes for priority and status
   - Include tier1/tier2 review fields

2. Create correction/queue_manager.py with CorrectionQueueManager class:
   - __init__(db_path) -> initialize SQLite connection
   - add_to_queue(item) -> add error to queue
   - get_next_for_tier1() -> get highest priority PENDING item
   - submit_tier1_correction(item_id, reviewer, correction)
   - get_next_for_tier2() -> sample 20% for validation
   - submit_tier2_validation(item_id, reviewer, validation)
   - resolve_consensus(item_id, resolution) -> expert resolution
   - get_resolved_corrections(limit) -> for retraining
   - get_queue_stats() -> dashboard metrics

3. Create correction/prodigy_review.py:
   - @prodigy.recipe("ner10-tier1-review")
   - Implement get_stream() to pull from queue
   - Implement update_db() to save corrections

4. Test queue workflow:
   - Add 10 items to queue with varying priorities
   - Retrieve next for tier1 -> verify highest priority first
   - Submit tier1 correction
   - Retrieve for tier2 -> verify 20% sampling
   - Submit tier2 validation (agreement)
   - Verify status = RESOLVED
   - Get queue stats -> verify counts

5. Integration test:
   - Run error detection -> generates errors
   - Errors auto-added to queue
   - Launch Prodigy: prodigy ner10-tier1-review corrections ./corrections_queue.jsonl
   - Annotate 5 items
   - Verify corrections saved to database

6. Git workflow:
   - git add correction/
   - git commit -m "feat(feedback): Implement correction queue system (LOOP-01)
   
   - Added SQLite-backed correction queue
   - Tier 1/2 review workflow with consensus resolution
   - Prodigy integration for human review
   - Priority-based queue ordering
   - Queue statistics dashboard
   - All tests passing
   
   Closes: LOOP-01, Addresses: GAP-01 Phase 2"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ Queue database operational
- ✅ Tier 1/2 workflow functional
- ✅ Prodigy interface works
- ✅ Priority ordering correct
- ✅ Queue stats accurate

OUTPUT:
- Show queue stats after adding 10 items
- Show Prodigy screenshot (if possible)
- Show git commit hash
- Confirm: "LOOP-01 complete, ready for LOOP-02"
```

**NEXT TASK AFTER COMPLETION**: LOOP-02 (Automated Retraining Trigger)

---

### LOOP-02: Automated Retraining Trigger

**TASK**: LOOP-02 - Automated Retraining Trigger  
**AGENT**: DATA_OPS  
**DURATION**: 3 days  
**DEPENDENCIES**: LOOP-01 (Correction Queue)

**EXACT PROMPT**:
```
Act as DATA_OPS. Implement LOOP-02: Automated Retraining Trigger (GAP-01 Phase 3).

CONTEXT:
- Correction queue (LOOP-01) is collecting resolved corrections
- We need automated triggers to retrain the model when conditions are met
- 5 trigger conditions: weekly, high correction rate, F1 drop, critical F1, manual

TASKS:
1. Install schedule library:
   - pip install schedule

2. Create training/retrain_trigger.py with RetrainingTrigger class:
   - check_triggers() -> checks all 5 trigger conditions
   - execute_retraining() -> runs retraining pipeline
   - run_scheduler() -> continuous monitoring

3. Implement 5 trigger conditions:
   - Trigger 1: Weekly (Monday 02:00 UTC)
   - Trigger 2: High correction rate (>100/week)
   - Trigger 3: F1 drop (>0.05 from previous)
   - Trigger 4: Critical F1 (<0.75)
   - Trigger 5: Manual (RETRAIN_NOW.flag file exists)

4. Implement retraining pipeline:
   - Get resolved corrections from queue (limit 1000)
   - Prepare training data (convert to spaCy format)
   - Retrain model (30 iterations)
   - Validate new model (will implement in LOOP-03)
   - Deploy if validation passes

5. Test triggers:
   - Test weekly trigger (mock datetime)
   - Test high correction rate (add 150 corrections)
   - Test F1 drop (mock F1 history)
   - Test critical F1 (set F1 to 0.70)
   - Test manual (create RETRAIN_NOW.flag)

6. Dry-run retraining:
   - Add 50 corrections to queue, mark as RESOLVED
   - Trigger retraining manually
   - Verify: corrections retrieved, training data prepared
   - (Don't actually retrain yet - validation gate not ready)

7. Git workflow:
   - git add training/retrain_trigger.py tests/test_retrain_trigger.py
   - git commit -m "feat(feedback): Implement automated retraining triggers (LOOP-02)
   
   - Added 5 retraining trigger conditions
   - Weekly scheduled retraining (Monday 02:00 UTC)
   - High correction rate trigger (>100/week)
   - F1 drop trigger (>0.05)
   - Critical F1 trigger (<0.75)
   - Manual override trigger
   - Continuous scheduler with hourly checks
   - All tests passing
   
   Closes: LOOP-02, Addresses: GAP-01 Phase 3"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ All 5 triggers operational
- ✅ Scheduler runs continuously
- ✅ Logging captures trigger events
- ✅ Dry-run successful

OUTPUT:
- Show trigger check results
- Show dry-run output
- Show git commit hash
- Confirm: "LOOP-02 complete, ready for LOOP-03"
```

**NEXT TASK AFTER COMPLETION**: LOOP-03 (Validation Loop + Deployment Gate)

---

### LOOP-03: Validation Loop + Deployment Gate

**TASK**: LOOP-03 - Validation Loop + Deployment Gate  
**AGENT**: QA_OFFICER  
**DURATION**: 3 days  
**DEPENDENCIES**: LOOP-02 (Retraining Trigger)

**EXACT PROMPT**:
```
Act as QA_OFFICER. Implement LOOP-03: Validation Loop + Deployment Gate (GAP-01 Phase 4).

CONTEXT:
- Retraining trigger (LOOP-02) can now retrain models
- We need a validation gate to ensure new models are better before deployment
- Held-out test set must NEVER be used in training

TASKS:
1. Create held-out test set:
   - Run: python validation/create_test_set.py
   - This will:
     * Load all annotated files
     * Stratified split (20% test, 80% train)
     * Save to test_set/ directory
     * Add test_set/ to .gitignore (CRITICAL)
   - Verify: test_set/ contains 18-20 files (20% of 91)

2. Create validation/deployment_gate.py with DeploymentGate class:
   - validate_model(model_path) -> runs validation
   - _check_no_regression(metrics) -> ensures no entity type regressed
   - Returns: {passes_gate, metrics, gates, recommendation}

3. Implement 4 deployment gates:
   - Gate 1: F1 >= 0.80
   - Gate 2: Precision >= 0.80
   - Gate 3: Recall >= 0.78
   - Gate 4: No regression (F1 drop < 0.03 for any entity type)

4. Test validation gate:
   - Create mock model with F1=0.82, Precision=0.81, Recall=0.79
   - Run validation -> should PASS all gates
   - Create mock model with F1=0.75
   - Run validation -> should FAIL (F1 gate)
   - Create mock model with regression (EQUIPMENT F1 drops 0.05)
   - Run validation -> should FAIL (regression gate)

5. Integrate with retraining:
   - Update training/retrain_trigger.py
   - Add _validate_model() call after retraining
   - If passes: deploy model, update metrics
   - If fails: rollback, send alert

6. End-to-end test:
   - Add 100 corrections to queue
   - Trigger retraining manually (touch RETRAIN_NOW.flag)
   - Wait for retraining to complete
   - Verify: validation runs, gates checked
   - If passes: new model deployed
   - If fails: old model retained

7. Git workflow:
   - git add validation/ .gitignore
   - git commit -m "feat(feedback): Implement validation loop and deployment gate (LOOP-03)
   
   - Created held-out test set (20% of data, never used in training)
   - Implemented 4-gate deployment validation
   - F1, Precision, Recall thresholds
   - Regression detection across all entity types
   - Integrated with retraining pipeline
   - Automatic rollback on validation failure
   - All tests passing
   
   Closes: LOOP-03, Addresses: GAP-01 Phase 4"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ Held-out test set created and gitignored
- ✅ All 4 gates operational
- ✅ Regression detection works
- ✅ Integration with retraining successful
- ✅ Failed validations trigger alerts

OUTPUT:
- Show test set statistics
- Show validation results on mock models
- Show end-to-end test output
- Show git commit hash
- Confirm: "LOOP-03 complete, core feedback loop operational, ready for OPT-01"
```

**NEXT TASK AFTER COMPLETION**: OPT-01 (Continuous Improvement Analytics)

---

### OPT-01: Continuous Improvement Analytics

**TASK**: OPT-01 - Continuous Improvement Analytics  
**AGENT**: ARCHITECT + QA_OFFICER  
**DURATION**: 4 days  
**DEPENDENCIES**: LOOP-03 (Validation Loop)

**EXACT PROMPT**:
```
Act as ARCHITECT and QA_OFFICER. Implement OPT-01: Continuous Improvement Analytics (GAP-01 Phase 5).

CONTEXT:
- Core feedback loop (LOOP-01/02/03) is operational
- We need analytics to identify weak entities and learn from corrections
- This enables proactive improvement, not just reactive fixes

TASKS:
1. Create analytics/weak_entity_analyzer.py with WeakEntityAnalyzer class:
   - identify_weak_entities() -> finds entity types with low F1 or high correction rate
   - _calculate_correction_rates() -> correction rate per entity type
   - _calculate_priority() -> prioritizes improvement efforts

2. Create analytics/pattern_learner.py with CorrectionPatternLearner class:
   - learn_patterns() -> extracts patterns from corrections
   - _find_common_false_positives() -> entities frequently marked incorrect
   - _find_common_false_negatives() -> entities frequently missed
   - _find_boundary_errors() -> wrong span issues

3. Create analytics/recommendation_generator.py:
   - generate_monthly_recommendations() -> creates action items
   - Combines weak entity analysis + pattern learning
   - Outputs: JSON report with prioritized action items

4. Test weak entity identification:
   - Mock metrics: EQUIPMENT F1=0.72, VULNERABILITY F1=0.85
   - Mock corrections: EQUIPMENT correction_rate=0.25
   - Run analyzer
   - Verify: EQUIPMENT identified as weak (F1 < 0.75 AND correction_rate > 0.20)

5. Test pattern learning:
   - Create 20 mock corrections with patterns:
     * 5 false positives: "Windows" labeled as EQUIPMENT (should be SOFTWARE)
     * 3 false negatives: missed "Stuxnet" as MALWARE
     * 2 boundary errors: "CVE-2021-44228" captured as "CVE-2021"
   - Run pattern learner
   - Verify: patterns correctly identified

6. Generate first monthly report:
   - Run: python analytics/recommendation_generator.py
   - Verify report includes:
     * Weak entities (top 5)
     * Common patterns (false pos/neg, boundary errors)
     * Action items (prioritized)
     * Expected improvement estimates

7. Git workflow:
   - git add analytics/
   - git commit -m "feat(analytics): Implement continuous improvement analytics (OPT-01)
   
   - Added weak entity identification
   - Pattern learning from corrections
   - Monthly recommendation generator
   - Prioritized action items
   - Expected improvement estimates
   - All tests passing
   
   Closes: OPT-01, Addresses: GAP-01 Phase 5"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ Weak entity identification works
- ✅ Pattern learning extracts insights
- ✅ Monthly reports generated
- ✅ Action items prioritized

OUTPUT:
- Show weak entity analysis results
- Show pattern learning output
- Show first monthly report
- Show git commit hash
- Confirm: "OPT-01 complete, Phase 0-1 complete (Weeks 1-4), ready for Phase 2"
```

**NEXT TASK AFTER COMPLETION**: SCHEMA-02 (Psychometric Entity Subtypes)

---

### SCHEMA-02: Psychometric Entity Subtypes

**TASK**: SCHEMA-02 - Psychometric Entity Subtypes  
**AGENT**: ARCHITECT + DATA_OPS  
**DURATION**: 5 days  
**DEPENDENCIES**: OPT-01 (Continuous Improvement)

**EXACT PROMPT**:
```
Act as ARCHITECT and DATA_OPS. Implement SCHEMA-02: Psychometric Entity Subtypes (GAP-02).

CONTEXT:
- Current schema has 12 broad labels (COGNITIVE_BIAS, EMOTION, etc.)
- We need to expand to 40+ labels with subtypes (NORMALCY_BIAS, ANXIETY, etc.)
- This enables Level 4 (Psychometric Layer) of the AEON architecture

TASKS:
1. Create schema_mapping_v2.json:
   - Expand each psychometric entity type with subtypes
   - COGNITIVE_BIAS: 7 subtypes (NORMALCY_BIAS, AVAILABILITY_BIAS, etc.)
   - THREAT_PERCEPTION: 3 subtypes (REAL_THREAT, IMAGINARY_THREAT, SYMBOLIC_THREAT)
   - EMOTION: 6 subtypes (ANXIETY, PANIC, DENIAL, COMPLACENCY, FRUSTRATION, SHOCK)
   - ATTACKER_MOTIVATION: 4 subtypes (MONEY, IDEOLOGY, COMPROMISE, EGO)
   - DEFENSE_MECHANISM: 4 subtypes (DENIAL, PROJECTION, RATIONALIZATION, SUBLIMATION)
   - SECURITY_CULTURE: 3 subtypes (MATURE, DEVELOPING, IMMATURE)
   - HISTORICAL_PATTERN: 3 subtypes (ORG_BEHAVIOR, SECTOR_BEHAVIOR, ATTACKER_BEHAVIOR)
   - FUTURE_THREAT_PREDICTION: 3 subtypes (TECH, BEHAVIORAL, GEO)
   - Total: 33 new labels

2. Update configs/train_config_v2.cfg:
   - Add all 40+ labels to [initialize.components.ner]
   - Update architecture if needed

3. Annotate examples for each subtype:
   - Goal: 500+ examples per subtype
   - Use LLM to classify existing <COGNITIVE_BIAS> tags into subtypes
   - Create annotation/annotate_subtypes.py
   - Run on Cognitive_Biases/ folder (652 existing annotations)
   - Manually review 100 examples for quality

4. Fine-tune model with subtypes:
   - Prepare training data with new labels
   - Train: python -m spacy train configs/train_config_v2.cfg --output models/ner10_v2 --paths.train corpus/train.spacy --paths.dev corpus/dev.spacy --gpu-id 0
   - Training time: ~2-3 hours on GPU

5. Evaluate per-subtype F1:
   - Run evaluation on dev set
   - Calculate F1 for each of the 33 new subtypes
   - Target: F1 > 0.70 for each subtype
   - If any subtype < 0.70: annotate 100 more examples, retrain

6. Test on real examples:
   - Text: "The CISO expressed concern about nation-state APTs while ignoring ransomware warnings"
   - Expected entities:
     * "concern" -> ANXIETY (EMOTION subtype)
     * "nation-state APTs" -> IMAGINARY_THREAT (THREAT_PERCEPTION subtype)
     * Implicit: AVAILABILITY_BIAS (COGNITIVE_BIAS subtype)

7. Git workflow:
   - git add schema_mapping_v2.json configs/train_config_v2.cfg annotation/annotate_subtypes.py models/ner10_v2/
   - git commit -m "feat(schema): Implement psychometric entity subtypes (SCHEMA-02)
   
   - Expanded schema from 12 to 40+ labels
   - Added 33 psychometric subtypes
   - Annotated 500+ examples per subtype
   - Fine-tuned model with new labels
   - Per-subtype F1 > 0.70
   - Enables Level 4 (Psychometric Layer)
   - All tests passing
   
   Closes: SCHEMA-02, Addresses: GAP-02"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ Schema expanded to 40+ labels
- ✅ 500+ examples per subtype
- ✅ Model trained with subtypes
- ✅ F1 > 0.70 for each subtype

OUTPUT:
- Show schema_mapping_v2.json structure
- Show per-subtype F1 scores
- Show test example predictions
- Show git commit hash
- Confirm: "SCHEMA-02 complete, ready for SCHEMA-03"
```

**NEXT TASK AFTER COMPLETION**: SCHEMA-03 (Relationship Extraction)

---

### SCHEMA-03: Relationship Extraction

**TASK**: SCHEMA-03 - Relationship Extraction  
**AGENT**: ARCHITECT  
**DURATION**: 4 days  
**DEPENDENCIES**: SCHEMA-02 (Psychometric Subtypes)

**EXACT PROMPT**:
```
Act as ARCHITECT. Implement SCHEMA-03: Relationship Extraction (GAP-03).

CONTEXT:
- Entity extraction is working (40+ labels)
- Neo4j schema has 171 relationship types
- We need to extract relationships between entities (TARGETS, EXPLOITS, USES, etc.)

TASKS:
1. Create extraction/relationship_extractor.py with RelationshipExtractor class:
   - Uses spaCy DependencyMatcher
   - Implements 5 relationship patterns:
     * TARGETS: THREAT_ACTOR -> SECTOR/ORGANIZATION/EQUIPMENT
     * USES_MALWARE: THREAT_ACTOR -> MALWARE
     * EXPLOITS: MALWARE -> VULNERABILITY
     * AFFECTS: VULNERABILITY -> EQUIPMENT
     * USES_TTP: ATTACK_PATTERN -> MITRE_TECHNIQUE

2. Implement dependency patterns:
   - Pattern 1 (TARGETS): actor -> verb(target/attack) -> target
   - Pattern 2 (USES_MALWARE): actor -> verb(use/deploy) -> malware
   - Pattern 3 (EXPLOITS): malware -> verb(exploit) -> vulnerability
   - Pattern 4 (AFFECTS): vulnerability -> verb(affect/impact) -> equipment
   - Pattern 5 (USES_TTP): pattern -> verb(use/implement) -> TTP

3. Test relationship extraction:
   - Test case 1: "APT29 targeted water utilities"
     * Expected: TARGETS(APT29, water utilities)
   - Test case 2: "APT29 used Cobalt Strike"
     * Expected: USES_MALWARE(APT29, Cobalt Strike)
   - Test case 3: "Cobalt Strike exploited CVE-2021-44228"
     * Expected: EXPLOITS(Cobalt Strike, CVE-2021-44228)
   - Test case 4: "CVE-2021-44228 affects Siemens S7-1200"
     * Expected: AFFECTS(CVE-2021-44228, Siemens S7-1200)

4. Evaluate on test set:
   - Create test set of 50 sentences with known relationships
   - Run extraction
   - Calculate: Precision, Recall, F1
   - Target: Precision > 0.80, Recall > 0.60

5. Integrate with main pipeline:
   - Update scripts/ingest_tags.py to extract relationships
   - Save relationships to separate file: corpus/relationships.jsonl
   - Format: {source, target, type, confidence}

6. Test end-to-end:
   - Process 10 files from Training_Data_Check_to_see/
   - Extract entities + relationships
   - Verify: relationships.jsonl contains valid relationships
   - Manually review 20 relationships for accuracy

7. Git workflow:
   - git add extraction/relationship_extractor.py tests/test_relationship_extraction.py corpus/relationships.jsonl
   - git commit -m "feat(extraction): Implement relationship extraction (SCHEMA-03)
   
   - Added DependencyMatcher-based relationship extraction
   - Implemented 5 relationship types
   - TARGETS, USES_MALWARE, EXPLOITS, AFFECTS, USES_TTP
   - Precision > 0.80, Recall > 0.60
   - Integrated with main pipeline
   - All tests passing
   
   Closes: SCHEMA-03, Addresses: GAP-03"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ 5 relationship types extracted
- ✅ Precision > 0.80
- ✅ Recall > 0.60
- ✅ Integrated with pipeline

OUTPUT:
- Show relationship extraction results on test cases
- Show precision/recall metrics
- Show sample relationships.jsonl
- Show git commit hash
- Confirm: "SCHEMA-03 complete, ready for SCHEMA-01"
```

**NEXT TASK AFTER COMPLETION**: SCHEMA-01 (Neo4j Systems Agent)

---

### SCHEMA-01: Neo4j Systems Agent

**TASK**: SCHEMA-01 - Neo4j "Systems" Agent  
**AGENT**: ARCHITECT  
**DURATION**: 3 days  
**DEPENDENCIES**: SCHEMA-03 (Relationship Extraction)

**EXACT PROMPT**:
```
Act as ARCHITECT. Implement SCHEMA-01: Neo4j "Systems" Agent (IMP-03).

CONTEXT:
- Schema mapping and relationship extraction are complete
- We need a validation agent that enforces Neo4j schema compliance
- This prevents hallucinations and ensures ontology alignment

TASKS:
1. Create agents/architect_agent.py with ArchitectAgent class:
   - validate_schema_compliance(entities) -> checks all entities against schema
   - _check_neo4j_existence(entity_text) -> queries Neo4j for existing entities
   - _is_valid_label(label) -> validates label against schema
   - Returns: {accepted, rejected, agent_confidence}

2. Implement 3 validation checks:
   - Check 1: Valid NER label? (label in schema_mapping_v2.json)
   - Check 2: Maps to Neo4j label? (label -> neo4j_labels mapping exists)
   - Check 3: Entity exists in Neo4j OR is novel but valid?

3. Test validation:
   - Test case 1: "Siemens S7-1200" with label "EQUIPMENT"
     * Check Neo4j -> exists as Equipment
     * Expected: ACCEPT, confidence=0.95, status=existing
   - Test case 2: "NewThreat" with label "THREAT_ACTOR"
     * Check Neo4j -> not found
     * Check schema -> THREAT_ACTOR is valid
     * Expected: ACCEPT, confidence=0.80, status=novel
   - Test case 3: "Something" with label "INVALID_LABEL"
     * Check schema -> INVALID_LABEL not in schema
     * Expected: REJECT, reason="Invalid label"

4. Test schema compliance:
   - Create test set of 100 entities (80 valid, 20 invalid)
   - Run validation
   - Verify: 0% false accepts (no invalid entities pass)
   - Verify: 100% true accepts (all valid entities pass)

5. Integrate with main pipeline:
   - Update scripts/ingest_tags.py
   - After entity extraction, run ArchitectAgent validation
   - Filter out rejected entities
   - Log rejection reasons

6. Test end-to-end:
   - Process 10 files with mix of valid/invalid entities
   - Verify: invalid entities rejected
   - Verify: valid entities accepted
   - Check logs for rejection reasons

7. Git workflow:
   - git add agents/architect_agent.py tests/test_architect_agent.py
   - git commit -m "feat(validation): Implement Neo4j Systems Agent (SCHEMA-01/IMP-03)
   
   - Added ArchitectAgent for schema validation
   - 3 validation checks: label validity, Neo4j mapping, entity existence
   - 100% schema compliance (0% false accepts)
   - Distinguishes existing vs. novel entities
   - Integrated with main pipeline
   - All tests passing
   
   Closes: SCHEMA-01, IMP-03"
   - git push origin main

ACCEPTANCE CRITERIA:
- ✅ Schema violations rejected (0% false accepts)
- ✅ Existing entities validated against Neo4j
- ✅ Novel entities accepted if schema-compliant
- ✅ Agent confidence > 0.80

OUTPUT:
- Show validation results on test cases
- Show schema compliance metrics
- Show end-to-end test output
- Show git commit hash
- Confirm: "SCHEMA-01/IMP-03 complete, Phase 2 complete (Weeks 5-6), ready for Phase 3 (Neural Swarm)"
```

**NEXT TASK AFTER COMPLETION**: Neural Swarm Phase 3 (refer to DETAILED_SWARM_PLAN.md)

---

## APPENDIX B: Git Workflow Best Practices

### Commit Message Format

All commits should follow this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding tests
- `docs`: Documentation
- `refactor`: Code refactoring
- `perf`: Performance improvement

**Scopes**:
- `feedback`: Feedback loop components
- `testing`: Test infrastructure
- `schema`: Schema and ontology
- `extraction`: Entity/relationship extraction
- `validation`: Validation and QA
- `analytics`: Analytics and reporting
- `swarm`: Neural Swarm components

**Example**:
```
feat(feedback): Implement error detection pipeline (CORE-03)

- Added 4 error detection mechanisms
- Low confidence detection (threshold: 0.70)
- Schema violation detection
- F1 degradation monitoring
- Relationship validation
- Detection accuracy: 95%+
- All tests passing

Closes: CORE-03, Addresses: GAP-01 Phase 1
```

### Pre-Commit Checklist

Before every commit:
1. ✅ Run tests: `pytest tests/ -v`
2. ✅ Check coverage: `pytest --cov=scripts --cov-report=term-missing`
3. ✅ Run linter: `flake8 scripts/ tests/`
4. ✅ Update logs/metrics if applicable
5. ✅ Update PROGRESS_LOG.md
6. ✅ Update TASKMASTER.md (mark task complete)

### Commit Workflow

```bash
# 1. Check status
git status

# 2. Add files
git add <files>

# 3. Commit with message
git commit -m "<message>"

# 4. Push to remote
git push origin main

# 5. Verify push
git log --oneline -1

# 6. Update PROGRESS_LOG.md
echo "| $(date '+%Y-%m-%d %H:%M') | **AGENT** | Task Name | ✅ Complete | \`file.py\` |" >> /home/jim/.gemini/antigravity/brain/6683fd3f-e978-454b-b385-d1391b4f26ce/PROGRESS_LOG.md

# 7. Commit progress log
git add /home/jim/.gemini/antigravity/brain/6683fd3f-e978-454b-b385-d1391b4f26ce/PROGRESS_LOG.md
git commit -m "docs: Update progress log"
git push origin main
```

---

## APPENDIX C: Multi-Agent Orchestration for Context Management

### Problem: Context Window Limits

Large implementation plans can exceed context windows. Use multi-agent orchestration to manage this.

### Solution: Agent Specialization

**Agent Roles**:
1. **COORDINATOR**: Manages overall workflow, delegates to specialists
2. **DATA_OPS**: Handles data processing, ingestion, pipelines
3. **ARCHITECT**: Handles schema, validation, Neo4j integration
4. **QA_OFFICER**: Handles testing, validation, quality gates
5. **RESEARCHER**: Handles web search, validation, research tasks

### Orchestration Pattern

**COORDINATOR Prompt**:
```
Act as COORDINATOR. You are managing the NER10 implementation.

CURRENT PHASE: Phase 0, Week 1
CURRENT TASK: CORE-02 (Unit Tests)
NEXT TASK: CORE-03 (Error Detection)

DELEGATION:
1. Delegate CORE-02 to DATA_OPS + QA_OFFICER
2. Monitor progress
3. When CORE-02 complete, delegate CORE-03 to DATA_OPS

CONTEXT MANAGEMENT:
- Keep only current task in context
- Reference COMPLETE_IMPLEMENTATION_PLAN.md for details
- Use exact prompts from Appendix A
- Update PROGRESS_LOG.md after each task

EXECUTE:
Delegate CORE-02 to DATA_OPS + QA_OFFICER using the exact prompt from Appendix A.
```

**Specialist Prompt** (DATA_OPS):
```
Act as DATA_OPS. You have been delegated CORE-02 by COORDINATOR.

TASK: CORE-02 - Unit Tests for Ingestion
CONTEXT: See COMPLETE_IMPLEMENTATION_PLAN.md, search for "CORE-02"
EXACT PROMPT: [Copy from Appendix A]

EXECUTE:
Follow the exact prompt. Report back to COORDINATOR when complete.
```

### Context Handoff Protocol

When a task is complete:

1. **Specialist** reports to **COORDINATOR**:
   ```
   TASK: CORE-02
   STATUS: COMPLETE ✅
   DELIVERABLES:
   - 30+ unit tests written
   - Coverage: 92%
   - All tests passing
   - Git commit: abc123
   
   NEXT TASK: CORE-03 (Error Detection)
   ```

2. **COORDINATOR** updates state:
   ```
   PROGRESS_LOG updated
   TASKMASTER updated (CORE-02 marked complete)
   
   DELEGATING NEXT TASK: CORE-03 to DATA_OPS
   ```

3. **COORDINATOR** delegates:
   ```
   Act as DATA_OPS. You have been delegated CORE-03.
   [Exact prompt from Appendix A]
   ```

### Benefits

- ✅ Each agent has focused context (only current task)
- ✅ No context window overflow
- ✅ Clear handoffs between tasks
- ✅ Progress tracking via COORDINATOR

---

## APPENDIX D: Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /____\
     /      \  Integration Tests (30%)
    /________\
   /          \  Unit Tests (60%)
  /__________\
```

### Test Coverage Targets

| Component | Unit Tests | Integration Tests | E2E Tests | Total Coverage |
|-----------|------------|-------------------|-----------|----------------|
| Ingestion | 90%+ | 80%+ | N/A | 90%+ |
| Error Detection | 95%+ | 85%+ | N/A | 95%+ |
| Correction Queue | 85%+ | 90%+ | 70%+ | 85%+ |
| Retraining | 80%+ | 90%+ | 80%+ | 85%+ |
| Validation | 90%+ | 95%+ | 90%+ | 90%+ |
| Neural Swarm | 75%+ | 80%+ | 85%+ | 80%+ |

### Test Execution Order

1. **Unit Tests** (fast, run on every commit)
   ```bash
   pytest tests/test_*.py -v
   ```

2. **Integration Tests** (medium, run before push)
   ```bash
   pytest tests/integration/ -v
   ```

3. **E2E Tests** (slow, run before deployment)
   ```bash
   pytest tests/e2e/ -v --slow
   ```

### Continuous Testing

```bash
# Watch mode (re-run on file change)
pytest-watch tests/

# Coverage report
pytest --cov=scripts --cov=agents --cov=correction --cov-report=html

# Open coverage report
open htmlcov/index.html
```

---

## APPENDIX E: Troubleshooting Guide

### Common Issues

#### Issue 1: Tests Failing After Code Change

**Symptoms**:
- `pytest tests/` shows failures
- Coverage drops

**Diagnosis**:
```bash
pytest tests/ -v --tb=short
```

**Solutions**:
1. Check if test expectations need updating
2. Verify code changes didn't break contracts
3. Add new tests for new functionality
4. Update mocks if dependencies changed

---

#### Issue 2: Git Push Rejected (Large Files)

**Symptoms**:
- `git push` fails with "file size exceeds limit"

**Diagnosis**:
```bash
git ls-files --others --exclude-standard | xargs du -sh
```

**Solutions**:
1. Check .gitignore includes large files (corpus/, training/, models/)
2. Remove from git cache: `git rm --cached <file>`
3. Add to .gitignore
4. Commit and push

---

#### Issue 3: Error Detection Not Flagging Errors

**Symptoms**:
- Known errors not appearing in corrections_queue.jsonl

**Diagnosis**:
```bash
python scripts/error_detection.py --debug
cat logs/error_detection.log
```

**Solutions**:
1. Check thresholds (confidence < 0.70 might be too strict)
2. Verify schema_mapping.json is loaded correctly
3. Check F1 thresholds are set
4. Verify predictions format matches expected

---

#### Issue 4: Retraining Not Triggering

**Symptoms**:
- Corrections accumulating but no retraining

**Diagnosis**:
```bash
python training/retrain_trigger.py --check-triggers
```

**Solutions**:
1. Check scheduler is running: `ps aux | grep retrain_trigger`
2. Verify trigger conditions: `python training/retrain_trigger.py --show-status`
3. Check logs: `cat logs/retraining.log`
4. Manual trigger: `touch RETRAIN_NOW.flag`

---

#### Issue 5: Validation Gate Always Failing

**Symptoms**:
- New models never pass validation

**Diagnosis**:
```bash
python validation/deployment_gate.py --validate models/latest --verbose
```

**Solutions**:
1. Check thresholds (F1 >= 0.80 might be too high initially)
2. Verify test set is representative
3. Check for data leakage (test set in training)
4. Review per-entity metrics: `cat metrics/validation_latest.json`

---

## APPENDIX F: Performance Optimization

### Ingestion Performance

**Current**: 198 files/sec  
**Target**: 300 files/sec

**Optimizations**:
1. Parallel processing: Use `multiprocessing.Pool`
2. Batch Neo4j queries: Query 100 entities at once
3. Cache schema mapping: Load once, reuse
4. Skip unchanged files: Check file hash

**Implementation**:
```python
# scripts/ingest_tags_parallel.py
from multiprocessing import Pool

def process_file_parallel(file_path):
    # Process single file
    pass

if __name__ == "__main__":
    files = list(Path(DATA_ROOT).rglob("*.md"))
    
    with Pool(processes=8) as pool:
        results = pool.map(process_file_parallel, files)
```

---

### Error Detection Performance

**Current**: ~5s per 100 predictions  
**Target**: ~2s per 100 predictions

**Optimizations**:
1. Vectorize confidence checks: Use NumPy
2. Batch Neo4j queries: Single query for all entities
3. Cache F1 scores: Update hourly, not per prediction

---

### Retraining Performance

**Current**: ~2 hours for 30 iterations  
**Target**: ~1 hour for 30 iterations

**Optimizations**:
1. Use GPU: `--gpu-id 0`
2. Reduce batch size: `--batch-size 64` (from 128)
3. Early stopping: Stop if F1 plateaus
4. Mixed precision: `--use-amp`

---

## APPENDIX G: Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, E2E)
- [ ] Coverage > 85% across all components
- [ ] Validation gate passing (F1 > 0.80)
- [ ] No regressions detected
- [ ] Documentation updated
- [ ] PROGRESS_LOG.md updated
- [ ] TASKMASTER.md shows all tasks complete
- [ ] Git repo clean (no uncommitted changes)
- [ ] All code reviewed

### Deployment Steps

1. **Backup current model**:
   ```bash
   cp -r models/current models/backup_$(date +%Y%m%d)
   ```

2. **Deploy new model**:
   ```bash
   cp -r models/ner10_v2 models/current
   ```

3. **Update metrics baseline**:
   ```bash
   cp metrics/validation_latest.json metrics/baseline.json
   ```

4. **Restart services**:
   ```bash
   systemctl restart ner10-pipeline
   systemctl restart ner10-scheduler
   ```

5. **Monitor for 24 hours**:
   ```bash
   tail -f logs/production.log
   ```

6. **Verify metrics**:
   ```bash
   python analytics/check_production_metrics.py
   ```

### Post-Deployment

- [ ] Production F1 > 0.80 (24h average)
- [ ] Error rate < 5%
- [ ] Throughput > 100 files/hour
- [ ] No critical errors in logs
- [ ] Correction queue size stable
- [ ] IAA > 0.85 (if human review active)

### Rollback Plan

If any post-deployment check fails:

```bash
# Stop services
systemctl stop ner10-pipeline ner10-scheduler

# Restore backup
rm -rf models/current
cp -r models/backup_$(date +%Y%m%d) models/current

# Restart services
systemctl start ner10-pipeline ner10-scheduler

# Alert team
python scripts/send_alert.py "Rollback executed: [reason]"
```

---

**END OF APPENDICES**

---

## Quick Reference: Task Sequence

1. ✅ **CORE-01**: Structured Logging (COMPLETE)
2. **CORE-02**: Unit Tests (2 days) → Next Prompt: Appendix A
3. **CORE-03**: Error Detection (5 days) → Next Prompt: Appendix A
4. **LOOP-01**: Correction Queue (4 days) → Next Prompt: Appendix A
5. **LOOP-02**: Retraining Trigger (3 days) → Next Prompt: Appendix A
6. **LOOP-03**: Validation Loop (3 days) → Next Prompt: Appendix A
7. **OPT-01**: Analytics (4 days) → Next Prompt: Appendix A
8. **SCHEMA-02**: Psychometric Subtypes (5 days) → Next Prompt: Appendix A
9. **SCHEMA-03**: Relationship Extraction (4 days) → Next Prompt: Appendix A
10. **SCHEMA-01**: Neo4j Agent (3 days) → Next Prompt: Appendix A
11. **Neural Swarm**: Weeks 7-10 → See DETAILED_SWARM_PLAN.md
12. **OPT-02**: Monitoring Dashboard (3 days)
13. **Production Deployment**: Week 12

**Total Duration**: 16 weeks  
**Current Status**: Week 1, CORE-01 complete, ready for CORE-02

---

**IMMEDIATE NEXT ACTION**:

Copy the exact prompt from **Appendix A, CORE-02** and execute it to begin Week 1, Day 3.

