import { contentService, type QuestionCreate } from './contentService'

export interface ImportError {
  row: number
  error: string
}

export interface ImportResult {
  success: boolean
  importedCount: number
  errors: ImportError[]
}

export interface CsvQuestionRow {
  text: string
  type: 'multiple_choice' | 'text' | 'interactive'
  options?: string
  correct_answer?: string
  difficulty_level: string
  misconception_id?: string
  time_seconds: string
}

class ImportService {
  /**
   * Parse CSV content into question rows
   */
  parseCSV(csvContent: string): CsvQuestionRow[] {
    const lines = csvContent.trim().split('\n')
    if (lines.length < 2) return []

    const headers = lines[0].split(',').map((h) => h.trim())
    const rows: CsvQuestionRow[] = []

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map((v) => v.trim())
      const row: Record<string, string> = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ''
      })
      rows.push(row as CsvQuestionRow)
    }

    return rows
  }

  /**
   * Convert CSV rows to question creates
   */
  convertCsvToQuestions(rows: CsvQuestionRow[], moduleId: string): { questions: QuestionCreate[]; errors: ImportError[] } {
    const questions: QuestionCreate[] = []
    const errors: ImportError[] = []

    rows.forEach((row, index) => {
      try {
        if (!row.text) {
          errors.push({ row: index + 2, error: 'Question text is required' })
          return
        }

        const question: QuestionCreate = {
          module_id: moduleId,
          content: {
            text: row.text,
            type: row.type || 'multiple_choice',
            options: row.options ? row.options.split('|') : undefined,
            correct_answer: row.correct_answer,
          },
          difficulty_level: parseInt(row.difficulty_level) || 3,
          target_misconception_id: row.misconception_id || undefined,
          estimated_time_sec: parseInt(row.time_seconds) || 60,
        }

        questions.push(question)
      } catch (err) {
        errors.push({ row: index + 2, error: `Failed to parse: ${err}` })
      }
    })

    return { questions, errors }
  }

  /**
   * Import questions from CSV string
   */
  async importFromCSV(moduleId: string, csvContent: string): Promise<ImportResult> {
    try {
      const rows = this.parseCSV(csvContent)
      const { questions, errors } = this.convertCsvToQuestions(rows, moduleId)

      if (questions.length === 0) {
        return {
          success: false,
          importedCount: 0,
          errors: errors.length > 0 ? errors : [{ row: 0, error: 'No valid questions found' }],
        }
      }

      const result = await contentService.bulkImportQuestions(moduleId, questions)

      return {
        success: true,
        importedCount: result.imported_count,
        errors,
      }
    } catch (err) {
      return {
        success: false,
        importedCount: 0,
        errors: [{ row: 0, error: `Import failed: ${err}` }],
      }
    }
  }

  /**
   * Import questions from JSON array
   */
  async importFromJSON(moduleId: string, jsonContent: string): Promise<ImportResult> {
    try {
      const data = JSON.parse(jsonContent)
      const questions: QuestionCreate[] = Array.isArray(data) ? data : data.questions || []

      // Validate and normalize questions
      const validQuestions: QuestionCreate[] = []
      const errors: ImportError[] = []

      questions.forEach((q, index) => {
        if (!q.content?.text) {
          errors.push({ row: index + 1, error: 'Question text is required' })
          return
        }
        validQuestions.push({
          ...q,
          module_id: moduleId,
        })
      })

      if (validQuestions.length === 0) {
        return {
          success: false,
          importedCount: 0,
          errors: errors.length > 0 ? errors : [{ row: 0, error: 'No valid questions found' }],
        }
      }

      const result = await contentService.bulkImportQuestions(moduleId, validQuestions)

      return {
        success: true,
        importedCount: result.imported_count,
        errors,
      }
    } catch (err) {
      return {
        success: false,
        importedCount: 0,
        errors: [{ row: 0, error: `Invalid JSON: ${err}` }],
      }
    }
  }

  /**
   * Generate CSV template for bulk import
   */
  generateCSVTemplate(): string {
    const headers = [
      'text',
      'type',
      'options',
      'correct_answer',
      'difficulty_level',
      'misconception_id',
      'time_seconds',
    ]
    const example = [
      'What is 1/4 + 1/4?',
      'multiple_choice',
      '1/8|1/4|1/2|2/4',
      '1/2',
      '3',
      'MATH-FRAC-ADD-01',
      '60',
    ]
    return [headers.join(','), example.join(',')].join('\n')
  }

  /**
   * Generate JSON template for bulk import
   */
  generateJSONTemplate(): string {
    const template = {
      questions: [
        {
          content: {
            text: 'What is 1/4 + 1/4?',
            type: 'multiple_choice',
            options: ['1/8', '1/4', '1/2', '2/4'],
            correct_answer: '1/2',
          },
          difficulty_level: 3,
          target_misconception_id: 'MATH-FRAC-ADD-01',
          estimated_time_sec: 60,
        },
      ],
    }
    return JSON.stringify(template, null, 2)
  }
}

export const importService = new ImportService()
