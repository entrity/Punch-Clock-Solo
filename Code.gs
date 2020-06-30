/*
  This code is loaded at script.google.com and deployed as a web app.
*/

var SHEET_ID = '19spKEmcL__K5nWRDlQWFEFiXiyX_ZdSorUPB5CjNVa4';

function logPunch (type) {
  var row = [type || 'Punch', new Date()];
  var sheet = SpreadsheetApp.openById(SHEET_ID);
  sheet.appendRow(row);
  return row;
}

function doGet(arg) {
  return ContentService.createTextOutput(logPunch(arg.parameter.t));
}
