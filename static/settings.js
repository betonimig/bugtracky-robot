/**
 * Type list of a bug.
 * @type {Array}
 */
var bugType = [
  'Bug',
  'Feature',
  'Customer Issue',
  'Internal Cleanup',
  'Process'
];

/**
 * Status list of a bug.
 * @type {Array}
 */
var bugStatus = [
  'New',
  'Assigned',
  'In Progress',
  'Verify'
];

/**
 * Priority range of a bug.
 * @type {Array}
 */
var bugPriority = [3, 5, 10];

/**
 * Attributes of a bug.
 * @type {Array}
 */
var attributes = [
  'Status',
  'Assignee',
  'Type',
  'Priority'
];


/**
 * Returns html string for options
 * @param {string} values Comma separated values.
 */
function getOptionHtml(index, values) {
  var attrib;
  switch (index) {
    case 0:
      attrib = bugStatus;
      break;
    case 1:
      break;
    case 2:
      attrib = bugType;
      break;
    case 3:
      attrib = bugPriority;
      break;
  }

  var html = '';
  var tplHtml = '';
  var fieldStr = attributes[index];
  var tplData = {
    id: 'bug-' + fieldStr.toLowerCase(),
    field: fieldStr + ':'
  };

  if (index == 1) { // Assignee
    tplHtml = _gel('tpl-bug-assignee').value;
  } else if (index == 3) { // Priority
    tplHtml = _gel('tpl-bug-priority').value;
    var labelsHtml = '', valuesHtml = '', len = attrib[parseInt(values)];
    for (var i = 0; i < len; i++) {
      labelsHtml += '<td align="center"><label for="P' + i +
          '">P' + i + '</label></td>';
      valuesHtml += '<td align="center"><input type="radio" value="P' + i +
          '" id="P' + i + '" name="bug-priority" disabled/>';
    }
    tplData.labels = labelsHtml;
    tplData.values = valuesHtml;
  } else {
    tplHtml = document.getElementById('tpl-bug-options').value;
    var indexes = values.split('|');
    for (var i = 0, len = indexes.length; i < len; i++) {
      var idx = indexes[i];
      html +=
          '<option value="' + attrib[idx] + '">' + attrib[idx] + '</option>';
    }
    tplData.options = html;
  }

  return tplHtml.supplant(tplData);
}

/**
 * Creates UI for buganizer app.
 * @param {string} statusValues Status options as comma separated string.
 * @param {boolean} isAssignee Flag to indicate whether
 *     assignee option to be added.
 * @param {string} typeValues Type options as comma separated string.
 * @param {string} priorityValues Priority options as comma separated string.
 */
function createUI(statusValues, isAssignee, typeValues, priortyValues) {
  var html = '<table cellspacing="5" cellpadding="5" width="100%">';
  if (statusValues != null && statusValues != '') {
    html += getOptionHtml(0, statusValues);
  }
  if (isAssignee != null && isAssignee != '') {
    html += getOptionHtml(1, isAssignee);
  }
  if (typeValues != null && typeValues != '') {
    html += getOptionHtml(2, typeValues);
  }
  if (priortyValues != null && priortyValues != '') {
    html += getOptionHtml(3, priortyValues);
  }
  html += '</table>';
  _gel('main-content').innerHTML = html;
  gadgets.window.adjustHeight();
}

/**
 * Checks for settings and display UI.
 * @param {Object} settingsData Settings object.
 */
function checkSettings(settingsData) {
  if (!settingsData) {
    return;
  }
  var status = settingsData.statusConfig;
  var type = settingsData.typeConfig;
  var assignee = settingsData.assigneeConfig;
  var priority = settingsData.priorityConfig;

  if (!status && !type && !assignee && !priority) {
    return;
  }
  createUI(status, assignee, type, priority);
}

/**
 * Pour the data in template string.
 * @param {Object} dataObject The data object to be filled in template
 *     string.
 * @return {string} The new string created from template string and
 *     filled with the given data.
 */
String.prototype.supplant = function(dataObject) {
  // Replaces {key} with the corresponding value in object.
  return this.replace(/{([^{}]+)}/g,
    function(match, firstSubMatch) {
      var replace = dataObject[firstSubMatch];
      return (typeof replace === 'string' ||
              typeof replace === 'number') ?
          replace : match;
    }
  );
};
