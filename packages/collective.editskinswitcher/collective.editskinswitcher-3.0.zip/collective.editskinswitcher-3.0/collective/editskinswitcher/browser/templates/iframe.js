// stretch the preview iframe to fit the edit interface

function calcHeight()
{ 
  var iframe = document.getElementById('editskinswitcher-preview');

  if (iframe) {
        var iframeWin = iframe.contentWindow || iframe.contentDocument.parentWindow;
        if (iframeWin.document.body) {
            iframe.height = iframeWin.document.documentElement.scrollHeight || iframeWin.document.body.scrollHeight;
        }
    }
}
