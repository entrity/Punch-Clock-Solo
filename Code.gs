/*
  This code is loaded at script.google.com and deployed as a web app.
*/

var SHEET_ID = '19spKEmcL__K5nWRDlQWFEFiXiyX_ZdSorUPB5CjNVa4';

function logPunch (type, msg) {
  var row = [type || 'Punch', new Date(), msg];
  SpreadsheetApp.openById(SHEET_ID).appendRow(row);
  /* temporary: copy for virginia */
  if (type == 'In' || type == 'Out') {
    var idForVirginia = '1C7ugz9HJImFdIg3hNZZEHkP5TQRdIrnZLTm_yeWxC0c';
    SpreadsheetApp.openById(idForVirginia).appendRow(row);
  }
  return row;
}

function doGet(arg) {
  return ContentService.createTextOutput(logPunch(arg.parameter.t, arg.parameter.m));
}
