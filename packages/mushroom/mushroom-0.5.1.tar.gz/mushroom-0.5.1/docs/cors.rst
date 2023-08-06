.. _cors:

****
CORS
****

In order to support Cross-Origin Resource Sharing mushroom utilizes the
Access-Control-Allow-Origin header and provides a fallback using a
so called CORS iframe. The CORS iframe works by setting the
document.domain in the parent frame and inside the iframe at the same
time. Once both frames have set their window.domain the parent frame can
use the XMLHttpRequest object of the CORS iframe and interact with the
server in a natural way.
