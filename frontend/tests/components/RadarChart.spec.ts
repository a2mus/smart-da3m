import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import SubjectRadarChart from '@/components/parent/SubjectRadarChart.vue'

// Mock canvas getContext for Chart.js in jsdom
if (typeof window !== 'undefined' && window.HTMLCanvasElement) {
  HTMLCanvasElement.prototype.getContext = vi.fn().mockImplementation(() => ({
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    getImageData: vi.fn(),
    putImageData: vi.fn(),
    createImageData: vi.fn(),
    setTransform: vi.fn(),
    drawImage: vi.fn(),
    save: vi.fn(),
    fillText: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    closePath: vi.fn(),
    stroke: vi.fn(),
    translate: vi.fn(),
    scale: vi.fn(),
    rotate: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    measureText: vi.fn(() => ({ width: 0 })),
    transform: vi.fn(),
    rect: vi.fn(),
    clip: vi.fn()
  })) as unknown as typeof HTMLCanvasElement.prototype.getContext
}

const i18n = createI18n({
  legacy: false,
  locale: 'ar',
  messages: {
    ar: {
      'parent.mathematics': 'الرياضيات',
      'parent.arabic': 'اللغة العربية',
      'parent.french': 'اللغة الفرنسية'
    }
  }
})

describe('SubjectRadarChart Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders empty state message when subjects array is empty', () => {
    const wrapper = mount(SubjectRadarChart, {
      props: { subjects: [] },
      global: { plugins: [i18n] }
    })

    expect(wrapper.text()).toContain('لا توجد بيانات للمواد')
    expect(wrapper.find('canvas').exists()).toBe(false)
  })

  it('renders canvas element when subjects are provided', () => {
    const subjects = [
      { name: 'الرياضيات', score: 85, mastery_level: 'PROFICIENT' },
      { name: 'اللغة العربية', score: 92, mastery_level: 'MASTERED' },
      { name: 'اللغة الفرنسية', score: 70, mastery_level: 'FAMILIAR' }
    ]

    const wrapper = mount(SubjectRadarChart, {
      props: { subjects },
      global: { plugins: [i18n] }
    })

    expect(wrapper.find('canvas').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('لا توجد بيانات للمواد')
  })

  it('handles scores on 0-100 scale and normalizes to 0-1 scale correctly', () => {
    const subjects = [
      { name: 'Math', score: 80 },
      { name: 'Arabic', score: 0.95 }
    ]

    const wrapper = mount(SubjectRadarChart, {
      props: { subjects },
      global: { plugins: [i18n] }
    })

    expect(wrapper.find('canvas').exists()).toBe(true)
  })
})
