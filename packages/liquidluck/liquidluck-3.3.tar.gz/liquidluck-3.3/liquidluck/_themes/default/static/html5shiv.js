(function(g,b){function k(){var a=e.elements;return"string"==typeof a?a.split(" "):a}function l(a){var c={},f=a.createElement,b=a.createDocumentFragment,d=b();a.createElement=function(a){if(!e.shivMethods)return f(a);var b;b=c[a]?c[a].cloneNode():m.test(a)?(c[a]=f(a)).cloneNode():f(a);return b.canHaveChildren&&!n.test(a)?d.appendChild(b):b};a.createDocumentFragment=Function("h,f","return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&("+k().join().replace(/\w+/g,function(a){f(a);
d.createElement(a);return'c("'+a+'")'})+");return n}")(e,d)}function h(a){var c;if(a.documentShived)return a;if(e.shivCSS&&!i){c=a.createElement("p");var b=a.getElementsByTagName("head")[0]||a.documentElement;c.innerHTML="x<style>article,aside,figcaption,figure,footer,header,hgroup,nav,section{display:block}mark{background:#FF0;color:#000}</style>";c=!!b.insertBefore(c.lastChild,b.firstChild)}j||(c=!l(a));if(c)a.documentShived=c;return a}var d=g.html5||{},n=/^<|^(?:button|form|map|select|textarea|object|iframe|option|optgroup)$/i,
m=/^<|^(?:a|b|button|code|div|fieldset|form|h1|h2|h3|h4|h5|h6|i|iframe|img|input|label|li|link|ol|option|p|param|q|script|select|span|strong|style|table|tbody|td|textarea|tfoot|th|thead|tr|ul)$/i,i,j;(function(){var a=b.createElement("a");a.innerHTML="<xyz></xyz>";i="hidden"in a;if(!(a=1==a.childNodes.length))a:{try{b.createElement("a")}catch(c){a=!0;break a}a=b.createDocumentFragment();a="undefined"==typeof a.cloneNode||"undefined"==typeof a.createDocumentFragment||"undefined"==typeof a.createElement}j=
a})();var e={elements:d.elements||"abbr article aside audio bdi canvas data datalist details figcaption figure footer header hgroup mark meter nav output progress section summary time video",shivCSS:!1!==d.shivCSS,shivMethods:!1!==d.shivMethods,type:"default",shivDocument:h};g.html5=e;h(b)})(this,document);
