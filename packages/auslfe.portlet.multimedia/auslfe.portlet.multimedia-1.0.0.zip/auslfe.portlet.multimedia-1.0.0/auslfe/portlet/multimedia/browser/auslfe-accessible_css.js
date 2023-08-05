/*
 * Super-trick file... we apply (only with JS enabled) a special additioal CSS class that hide
 * our images, in this way we do not get bad effects on page load.
 * 
 * We use JS, so not js-able browsers will not see this class, and Javascript enabled ones
 * will remove this class from portlet when images are ready.
 */

document.write('<style type="text/css">.hideFlag img {display: none}</style>');
