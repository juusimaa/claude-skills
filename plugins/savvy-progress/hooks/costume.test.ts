import { expect, mock, test } from 'claude-code/testing'

const PLUGIN = 'savvy-progress'
const pane = { title: '', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 30 }, view: {} } as const

// /orchestrate's workers wear the costume of the savvy tier matching their effort.
for (const [type, costume] of [
  ['orchestrate:haiku-worker', 'light'],
  ['orchestrate:sonnet-worker', 'medium'],
  ['general-purpose', 'other'],
] as const) {
  test(`costume: ${type} wears ${costume}`, async ($, on) => {
    mock.clock(on)
    on('ui.open', () => ({ value: { isPlaced: true } }))
    on('agent.spawn', () => ({ model: 'claude-haiku-5-5', agentId: 'a1' }))
    await $.agent.spawn({ tool_use_id: 't1', prompt: 'p', description: 'Work', subagentType: type, provider: 'engine', parentModel: 'claude-opus-5-5', background: false, fork: false } as never)
    const ui = await $.ui.mount({ plugin: PLUGIN, surface: 'desktop', component: 'Pane', requestId: 'savvy-agents', props: pane })
    const drawn = (await ui.findAll({ type: 'Svg' })).map(el => String(el.props.source)).join('')
    expect(drawn).toContain(`class="c-${costume} run"`)
  })
}
