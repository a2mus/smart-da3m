import pluginVue from 'eslint-plugin-vue'
import globals from 'globals'

export default [
  {
    ignores: ['dist/**', 'node_modules/**', 'coverage/**', 'public/**']
  },
  ...pluginVue.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    rules: {
      'vue/no-restricted-class': [
        'error',
        'bg-white', 'bg-black',
        'text-white', 'text-black',
        'pl-0', 'pl-1', 'pl-2', 'pl-3', 'pl-4', 'pl-5', 'pl-6', 'pl-8', 'pl-10', 'pl-12', 'pl-16', 'pl-20', 'pl-24', 'pl-32', 'pl-max', 'pl-auto',
        'pr-0', 'pr-1', 'pr-2', 'pr-3', 'pr-4', 'pr-5', 'pr-6', 'pr-8', 'pr-10', 'pr-12', 'pr-16', 'pr-20', 'pr-24', 'pr-32', 'pr-max', 'pr-auto',
        'ml-0', 'ml-1', 'ml-2', 'ml-3', 'ml-4', 'ml-5', 'ml-6', 'ml-8', 'ml-10', 'ml-12', 'ml-16', 'ml-20', 'ml-24', 'ml-32', 'ml-max', 'ml-auto',
        '-ml-1', '-ml-2', '-ml-3', '-ml-4', '-ml-5', '-ml-6', '-ml-8', '-ml-10', '-ml-12', '-ml-16', '-ml-20', '-ml-24', '-ml-32',
        'mr-0', 'mr-1', 'mr-2', 'mr-3', 'mr-4', 'mr-5', 'mr-6', 'mr-8', 'mr-10', 'mr-12', 'mr-16', 'mr-20', 'mr-24', 'mr-32', 'mr-max', 'mr-auto',
        '-mr-1', '-mr-2', '-mr-3', '-mr-4', '-mr-5', '-mr-6', '-mr-8', '-mr-10', '-mr-12', '-mr-16', '-mr-20', '-mr-24', '-mr-32',
        'left-0', 'left-1', 'left-2', 'left-3', 'left-4', 'left-5', 'left-6', 'left-8', 'left-10', 'left-12', 'left-16', 'left-20', 'left-24', 'left-32', 'left-auto', 'left-1/2', 'left-full',
        '-left-1', '-left-2', '-left-3', '-left-4', '-left-5', '-left-6', '-left-8', '-left-10', '-left-12', '-left-16', '-left-20', '-left-24', '-left-32', '-left-1/2', '-left-full',
        'right-0', 'right-1', 'right-2', 'right-3', 'right-4', 'right-5', 'right-6', 'right-8', 'right-10', 'right-12', 'right-16', 'right-20', 'right-24', 'right-32', 'right-auto', 'right-1/2', 'right-full',
        '-right-1', '-right-2', '-right-3', '-right-4', '-right-5', '-right-6', '-right-8', '-right-10', '-right-12', '-right-16', '-right-20', '-right-24', '-right-32', '-right-1/2', '-right-full'
      ],
      'vue/multi-word-component-names': 'off'
    }
  }
]
