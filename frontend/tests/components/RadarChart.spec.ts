import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import SubjectRadarChart from '@/components/parent/SubjectRadarChart.vue'

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {
      'parent.mathematics': 'الرياضيات',
      'parent.arabic': 'اللغة العربية',
      'parent.french': 'اللغة الفرنسية',
      'parent.science': 'العلوم',
      'parent.subjects': 'المواد الدراسية',
    },
    fr: {
      'parent.mathematics': 'Mathématiques',
      'parent.arabic': 'Arabe',
      'parent.french': 'Français',
      'parent.science': 'Sciences',
      'parent.subjects': 'Matières',
    },
  },
})

describe('SubjectRadarChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Component Rendering', () => {
    it('renders the radar chart container', () => {
      const wrapper = mount(SubjectRadarChart, {
        props: {
          subjects: [],
        },
        global: { plugins: [i18n] },
      })

      expect(wrapper.find('[data-testid="radar-chart"]').exists()).toBe(true)
    })

    it('renders with empty state when no subjects', () => {
      const wrapper = mount(SubjectRadarChart, {
        props: { subjects: [] },
        global: { plugins: [i18n] },
      })

      expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true)
    })

    it('renders chart when subjects provided', () => {
      const subjects = [
        { name: 'Mathematics', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
        { name: 'French', score: 78, mastery_level: 'FAMILIAR' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      expect(wrapper.find('[data-testid="chart-svg"]').exists()).toBe(true)
    })
  })

  describe('Chart Data Processing', () => {
    it('normalizes scores to 0-100 range', () => {
      const subjects = [
        { name: 'Math', score: 0.85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 0.92, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      // Component should handle both 0-1 and 0-100 scales
      const processedData = wrapper.vm.processedSubjects
      expect(processedData[0].normalizedScore).toBe(85)
      expect(processedData[1].normalizedScore).toBe(92)
    })

    it('limits to maximum 6 subjects for readability', () => {
      const subjects = Array(8).fill(null).map((_, i) => ({
        name: `Subject ${i}`,
        score: 50 + i,
        mastery_level: 'FAMILIAR',
      }))

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const processedData = wrapper.vm.processedSubjects
      expect(processedData.length).toBeLessThanOrEqual(6)
    })
  })

  describe('SVG Chart Rendering', () => {
    it('renders correct number of axes', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
        { name: 'French', score: 78, mastery_level: 'FAMILIAR' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const axes = wrapper.findAll('[data-testid="radar-axis"]')
      expect(axes.length).toBe(3)
    })

    it('renders data polygon', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
        { name: 'French', score: 78, mastery_level: 'FAMILIAR' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      expect(wrapper.find('[data-testid="radar-polygon"]').exists()).toBe(true)
    })

    it('renders concentric grid circles', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const gridCircles = wrapper.findAll('[data-testid="grid-circle"]')
      expect(gridCircles.length).toBeGreaterThanOrEqual(3)
    })

    it('renders subject labels', () => {
      const subjects = [
        { name: 'Mathematics', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      expect(wrapper.text()).toContain('Mathematics')
      expect(wrapper.text()).toContain('Arabic')
    })
  })

  describe('Color Coding', () => {
    it('uses green color for high scores (80+)', () => {
      const subjects = [
        { name: 'Math', score: 95, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const polygon = wrapper.find('[data-testid="radar-polygon"]')
      const fill = polygon.attributes('fill')
      expect(fill).toContain('green') || expect(fill).toContain('22c55e')
    })

    it('uses yellow color for medium scores (50-79)', () => {
      const subjects = [
        { name: 'Math', score: 65, mastery_level: 'FAMILIAR' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const polygon = wrapper.find('[data-testid="radar-polygon"]')
      const fill = polygon.attributes('fill')
      expect(fill).toContain('yellow') || expect(fill).toContain('eab308')
    })

    it('uses red color for low scores (<50)', () => {
      const subjects = [
        { name: 'Math', score: 35, mastery_level: 'ATTEMPTED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const polygon = wrapper.find('[data-testid="radar-polygon"]')
      const fill = polygon.attributes('fill')
      expect(fill).toContain('red') || expect(fill).toContain('ef4444')
    })
  })

  describe('Interactivity', () => {
    it('emits event when clicking on a subject area', async () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const subjectPoint = wrapper.find('[data-testid="subject-point"]')
      if (subjectPoint.exists()) {
        await subjectPoint.trigger('click')
        expect(wrapper.emitted('select-subject')).toBeTruthy()
      }
    })
  })

  describe('Accessibility', () => {
    it('has aria-label for chart', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const chart = wrapper.find('[data-testid="radar-chart"]')
      expect(chart.attributes('aria-label')).toBeTruthy()
    })

    it('renders text alternatives for visual data', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
        { name: 'Arabic', score: 92, mastery_level: 'MASTERED' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      // Should have screen reader friendly data table
      expect(wrapper.find('[data-testid="chart-data-table"]').exists() ||
             wrapper.find('[role="img"]').exists()).toBe(true)
    })
  })

  describe('Mobile Responsiveness', () => {
    it('adapts size for mobile viewport', () => {
      const subjects = [
        { name: 'Math', score: 85, mastery_level: 'PROFICIENT' },
      ]

      const wrapper = mount(SubjectRadarChart, {
        props: { subjects },
        global: { plugins: [i18n] },
      })

      const svg = wrapper.find('svg')
      expect(svg.exists()).toBe(true)

      // Should have viewBox for scaling
      expect(svg.attributes('viewBox')).toBeTruthy()
    })
  })
})
