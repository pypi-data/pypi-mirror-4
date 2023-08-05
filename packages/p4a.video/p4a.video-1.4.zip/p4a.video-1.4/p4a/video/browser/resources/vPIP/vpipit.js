/* vpipit version 0.03 
 * - If text link, open in ThickBox
 * 
 * Initialize the containing DIV and store base information in aDIVs
 * 
 * New:
 *   - Change to X11 license compatible with GPL
 * 
 * License (X11 Licnese)
 * ===================================================================
 *  Copyright 2006-2007  Enric Teller  (email: enric@vpip.org)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy 
 * of this software and associated documentation files (the "Software"), to 
 * deal in the Software without restriction, including without limitation the 
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
 * sell copies of the Software, and to permit persons to whom the Software is 
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in 
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.

 * Except as contained in this notice, the name of the author or copyright 
 * holders shall not be used in advertising or otherwise to promote the sale, 
 * use or other dealings in this Software without prior written authorization 
 * from the author or copyright holders.
 * 
 * ===================================================================
 * 
 */
 
function vPIPIt() {
	if (typeof vPIPPlayer.isMovieFile == "function") {
	   var oLinks;
		var i, j;
		
	   oLinks = document.getElementsByTagName("a");
	   for (i = 0; i < oLinks.length; i++) {
	   		if (oLinks[i].onclick == undefined || oLinks[i].onclick == null) {
		   		var movieType = vPIPPlayer.isMovieFile(oLinks[i]);
			   	
		      	if (movieType != null) {
			      	if (movieType.sMediaFormat.length > 0) {
						var byImage = false;
		   				var children = oLinks[i].childNodes;
		   				var imgChild;
						for (j=0; j < children.length; j++) {
							if (children[j].nodeName.toLowerCase() == "img") {
								imgChild = children[j];
								byImage = true;
								break;
							}
						}
						if (byImage) {
							var videoWidth = imgChild.width;
							var videoHeight = imgChild.height;
							oLinks[i].onclick = new Function("vPIPPlay(this,'width=" + videoWidth + ",height=" + videoHeight + "'); return false;");
						}
						else {
							oLinks[i].onclick = new Function("vPIPPlay(this, '', '', 'active=true'); return false;");
						}
			      	}
				}
	   		}
		}
	}
}


function addEvent(obj, evType, fn){
	if (obj.addEventListener) {
		obj.addEventListener(evType, fn, false);
		return true;
	} else if (obj.attachEvent){
		var r = obj.attachEvent("on"+evType, fn);
		return r;
	} else {
		return false;
	}
}

//Run vPIPInit on body load
addEvent(window, 'load', vPIPIt);
