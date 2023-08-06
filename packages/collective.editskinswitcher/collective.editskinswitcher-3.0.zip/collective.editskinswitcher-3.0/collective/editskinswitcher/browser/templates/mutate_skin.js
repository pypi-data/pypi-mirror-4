// Disable links in previewed iframe so that it doesn't mash up the interface ... 

function hideLinks() {
    for (var i=0; i<document.links.length; i++) {
        document.links[i].href = "javascript:;";
    }

    for (var f = 0; (formnode = document.getElementsByTagName('form').item(f)); f++) {
        for (var j = 0; (inputnode = formnode.getElementsByTagName('input').item(j)); j++) {
            inputnode.disabled = 'true';
        }
    }

   if(document.createElement) { //W3C Dom method.
        var myInput = document.createElement("input");
        myInput.setAttribute('name', 'mutate_skin');
        myInput.setAttribute('type', 'hidden');
        myInput.setAttribute('value', 'default');

        for (var i=0; i<document.forms.length; i++) {
            document.forms[i].appendChild(myInput);
        }
    }
}

if (window.addEventListener) window.addEventListener("load",hideLinks,false);
else if (window.attachEvent) window.attachEvent("onload",hideLinks);

