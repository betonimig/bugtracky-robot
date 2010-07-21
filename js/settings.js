var fields = [
 {label: 'Type',
  type: 'dropdown',
  values: ['Bug', 'Feature Request', 'Task']},
 {label: 'Status',
  type: 'dropdown',
  values: ['New', 'Assigned', 'In Progress', 'Fixed', 'WontFix']},
 {label: 'Assignee',
  type: 'text',
  autocomplete: usernames,
  values: ''},
 {label: 'Priority',
  type: 'radio',
  values: ['P0', 'P1', 'P2', 'P3']}
]
