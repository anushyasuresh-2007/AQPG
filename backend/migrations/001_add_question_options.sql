-- ============================================================================
-- Migration: Add question_options table for MCQ choices
-- Decision 1B: Separate table instead of storing JSON in numerical_data
-- 
-- Run ONCE against your MySQL database:
--   mysql -u <user> -p <dbname> < backend/migrations/001_add_question_options.sql
-- ============================================================================

-- Create question_options table
CREATE TABLE IF NOT EXISTS `question_options` (
    `id`           INT           NOT NULL AUTO_INCREMENT,
    `question_id`  INT           NOT NULL,
    `option_label` VARCHAR(5)    NOT NULL COMMENT 'A, B, C, D, or E',
    `option_text`  TEXT          NOT NULL,
    `is_correct`   TINYINT(1)    NOT NULL DEFAULT 0 COMMENT '1 if this is the correct answer',
    PRIMARY KEY (`id`),
    INDEX `idx_question_options_question_id` (`question_id`),
    CONSTRAINT `fk_question_options_question`
        FOREIGN KEY (`question_id`)
        REFERENCES `questions` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    -- Prevent duplicate labels for the same question
    UNIQUE KEY `uq_question_option_label` (`question_id`, `option_label`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='MCQ answer choices for questions with question_type = MCQ';

-- ============================================================================
-- Verify the migration succeeded
-- ============================================================================
SELECT 
    TABLE_NAME,
    TABLE_COMMENT,
    ENGINE,
    TABLE_COLLATION
FROM 
    information_schema.TABLES
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'question_options';
