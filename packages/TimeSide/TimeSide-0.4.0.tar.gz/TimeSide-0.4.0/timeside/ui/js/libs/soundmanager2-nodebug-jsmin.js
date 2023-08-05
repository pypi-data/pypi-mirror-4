/** @license

 SoundManager 2: JavaScript Sound for the Web
 ----------------------------------------------
 http://schillmania.com/projects/soundmanager2/

 Copyright (c) 2007, Scott Schiller. All rights reserved.
 Code provided under the BSD License:
 http://schillmania.com/projects/soundmanager2/license.txt

 V2.97a.20110424
*/
(function(Y){function M(M,X){function i(c){return function(a){return!this._t||!this._t._a?null:c.call(this,a)}}function pa(){if(c.debugURLParam.test(N))c.debugMode=!0}this.flashVersion=8;this.debugFlash=this.debugMode=!1;this.useConsole=!0;this.waitForWindowLoad=this.consoleOnly=!1;this.nullURL="about:blank";this.allowPolling=!0;this.useFastPolling=!1;this.useMovieStar=!0;this.bgColor="#ffffff";this.useHighPerformance=!1;this.flashPollingInterval=null;this.flashLoadTimeout=1E3;this.wmode=null;this.allowScriptAccess=
"always";this.useHTML5Audio=this.useFlashBlock=!1;this.html5Test=/^probably$/i;this.useGlobalHTML5Audio=!0;this.requireFlash=!1;this.audioFormats={mp3:{type:['audio/mpeg; codecs="mp3"',"audio/mpeg","audio/mp3","audio/MPA","audio/mpa-robust"],required:!0},mp4:{related:["aac","m4a"],type:['audio/mp4; codecs="mp4a.40.2"',"audio/aac","audio/x-m4a","audio/MP4A-LATM","audio/mpeg4-generic"],required:!0},ogg:{type:["audio/ogg; codecs=vorbis"],required:!1},wav:{type:['audio/wav; codecs="1"',"audio/wav","audio/wave",
"audio/x-wav"],required:!1}};this.defaultOptions={autoLoad:!1,stream:!0,autoPlay:!1,loops:1,onid3:null,onload:null,whileloading:null,onplay:null,onpause:null,onresume:null,whileplaying:null,onstop:null,onfailure:null,onfinish:null,onbeforefinish:null,onbeforefinishtime:5E3,onbeforefinishcomplete:null,onjustbeforefinish:null,onjustbeforefinishtime:200,multiShot:!0,multiShotEvents:!1,position:null,pan:0,type:null,usePolicyFile:!1,volume:100};this.flash9Options={isMovieStar:null,usePeakData:!1,useWaveformData:!1,
useEQData:!1,onbufferchange:null,ondataerror:null};this.movieStarOptions={bufferTime:3,serverURL:null,onconnect:null,duration:null};this.version=null;this.versionNumber="V2.97a.20110424";this.movieURL=null;this.url=M||null;this.altURL=null;this.enabled=this.swfLoaded=!1;this.o=null;this.movieID="sm2-container";this.id=X||"sm2movie";this.swfCSS={swfBox:"sm2-object-box",swfDefault:"movieContainer",swfError:"swf_error",swfTimedout:"swf_timedout",swfLoaded:"swf_loaded",swfUnblocked:"swf_unblocked",sm2Debug:"sm2_debug",
highPerf:"high_performance",flashDebug:"flash_debug"};this.oMC=null;this.sounds={};this.soundIDs=[];this.muted=!1;this.debugID="soundmanager-debug";this.debugURLParam=/([#?&])debug=1/i;this.didFlashBlock=this.specialWmodeCase=!1;this.filePattern=null;this.filePatterns={flash8:/\.mp3(\?.*)?$/i,flash9:/\.mp3(\?.*)?$/i};this.baseMimeTypes=/^\s*audio\/(?:x-)?(?:mp(?:eg|3))\s*(?:$|;)/i;this.netStreamMimeTypes=/^\s*audio\/(?:x-)?(?:mp(?:eg|3))\s*(?:$|;)/i;this.netStreamTypes=["aac","flv","mov","mp4","m4v",
"f4v","m4a","mp4v","3gp","3g2"];this.netStreamPattern=RegExp("\\.("+this.netStreamTypes.join("|")+")(\\?.*)?$","i");this.mimePattern=this.baseMimeTypes;this.features={buffering:!1,peakData:!1,waveformData:!1,eqData:!1,movieStar:!1};this.sandbox={};this.hasHTML5=null;this.html5={usingFlash:null};this.ignoreFlash=!1;var Z,c=this,y,n=navigator.userAgent,h=Y,N=h.location.href.toString(),k=this.flashVersion,g=document,$,O,r=[],E=!1,F=!1,m=!1,t=!1,qa=!1,G,o,aa,u,z,ba,P,ra,ca,v,sa,H,A,da,ea,Q,fa,ta,ua,R,
va,I=null,ga=null,w,ha,B,S,T,ia,j,U=!1,ja=!1,wa,xa,x=null,ya,V,p=!1,J,s,ka,za,l,Da=Array.prototype.slice,K=!1,la,C,Aa,Ba=n.match(/pre\//i),Ea=n.match(/(ipad|iphone|ipod)/i);n.match(/mobile/i);var q=n.match(/msie/i),Fa=n.match(/webkit/i),L=n.match(/safari/i)&&!n.match(/chrome/i),Ga=n.match(/opera/i),ma=!N.match(/usehtml5audio/i)&&!N.match(/sm2\-ignorebadua/i)&&L&&n.match(/OS X 10_6_([3-9])/i),na=typeof g.hasFocus!=="undefined"?g.hasFocus():null,D=typeof g.hasFocus==="undefined"&&L,Ca=!D;this._use_maybe=
N.match(/sm2\-useHTML5Maybe\=1/i);this._overHTTP=g.location?g.location.protocol.match(/http/i):null;this._http=!this._overHTTP?"http:":"";this.useAltURL=!this._overHTTP;this._global_a=null;if(Ea||Ba)c.useHTML5Audio=!0,c.ignoreFlash=!0,c.useGlobalHTML5Audio&&(K=!0);if(Ba||this._use_maybe)c.html5Test=/^(probably|maybe)$/i;this.supported=this.ok=function(){return x?m&&!t:c.useHTML5Audio&&c.hasHTML5};this.getMovie=function(c){return q?h[c]:L?y(c)||g[c]:y(c)};this.createSound=function(b){function a(){e=
S(e);c.sounds[d.id]=new Z(d);c.soundIDs.push(d.id);return c.sounds[d.id]}var e=null,f=null,d=null;if(!m||!c.ok())return ia("soundManager.createSound(): "+w(!m?"notReady":"notOK")),!1;arguments.length===2&&(b={id:arguments[0],url:arguments[1]});d=e=o(b);if(j(d.id,!0))return c.sounds[d.id];if(V(d))f=a(),f._setup_html5(d);else{if(k>8&&c.useMovieStar){if(d.isMovieStar===null)d.isMovieStar=d.serverURL||d.type&&d.type.match(c.netStreamPattern)||d.url.match(c.netStreamPattern)?!0:!1;if(d.isMovieStar&&d.usePeakData)d.usePeakData=
!1}d=T(d,"soundManager.createSound(): ");f=a();if(k===8)c.o._createSound(d.id,d.onjustbeforefinishtime,d.loops||1,d.usePolicyFile);else if(c.o._createSound(d.id,d.url,d.onjustbeforefinishtime,d.usePeakData,d.useWaveformData,d.useEQData,d.isMovieStar,d.isMovieStar?d.bufferTime:!1,d.loops||1,d.serverURL,d.duration||null,d.autoPlay,!0,d.autoLoad,d.usePolicyFile),!d.serverURL)f.connected=!0,d.onconnect&&d.onconnect.apply(f);(d.autoLoad||d.autoPlay)&&!d.serverURL&&f.load(d)}d.autoPlay&&!d.serverURL&&f.play();
return f};this.destroySound=function(b,a){if(!j(b))return!1;var e=c.sounds[b],f;e._iO={};e.stop();e.unload();for(f=0;f<c.soundIDs.length;f++)if(c.soundIDs[f]===b){c.soundIDs.splice(f,1);break}a||e.destruct(!0);delete c.sounds[b];return!0};this.load=function(b,a){if(!j(b))return!1;return c.sounds[b].load(a)};this.unload=function(b){if(!j(b))return!1;return c.sounds[b].unload()};this.start=this.play=function(b,a){if(!m||!c.ok())return ia("soundManager.play(): "+w(!m?"notReady":"notOK")),!1;if(!j(b))return a instanceof
Object||(a={url:a}),a&&a.url?(a.id=b,c.createSound(a).play()):!1;return c.sounds[b].play(a)};this.setPosition=function(b,a){if(!j(b))return!1;return c.sounds[b].setPosition(a)};this.stop=function(b){if(!j(b))return!1;return c.sounds[b].stop()};this.stopAll=function(){for(var b in c.sounds)c.sounds[b]instanceof Z&&c.sounds[b].stop()};this.pause=function(b){if(!j(b))return!1;return c.sounds[b].pause()};this.pauseAll=function(){for(var b=c.soundIDs.length;b--;)c.sounds[c.soundIDs[b]].pause()};this.resume=
function(b){if(!j(b))return!1;return c.sounds[b].resume()};this.resumeAll=function(){for(var b=c.soundIDs.length;b--;)c.sounds[c.soundIDs[b]].resume()};this.togglePause=function(b){if(!j(b))return!1;return c.sounds[b].togglePause()};this.setPan=function(b,a){if(!j(b))return!1;return c.sounds[b].setPan(a)};this.setVolume=function(b,a){if(!j(b))return!1;return c.sounds[b].setVolume(a)};this.mute=function(b){var a=0;typeof b!=="string"&&(b=null);if(b){if(!j(b))return!1;return c.sounds[b].mute()}else{for(a=
c.soundIDs.length;a--;)c.sounds[c.soundIDs[a]].mute();c.muted=!0}return!0};this.muteAll=function(){c.mute()};this.unmute=function(b){typeof b!=="string"&&(b=null);if(b){if(!j(b))return!1;return c.sounds[b].unmute()}else{for(b=c.soundIDs.length;b--;)c.sounds[c.soundIDs[b]].unmute();c.muted=!1}return!0};this.unmuteAll=function(){c.unmute()};this.toggleMute=function(b){if(!j(b))return!1;return c.sounds[b].toggleMute()};this.getMemoryUse=function(){if(k===8)return 0;if(c.o)return parseInt(c.o._getMemoryUse(),
10)};this.disable=function(b){typeof b==="undefined"&&(b=!1);if(t)return!1;t=!0;for(var a=c.soundIDs.length;a--;)ua(c.sounds[c.soundIDs[a]]);G(b);l.remove(h,"load",z);return!0};this.canPlayMIME=function(b){var a;c.hasHTML5&&(a=J({type:b}));return!x||a?a:b?b.match(c.mimePattern)?!0:!1:null};this.canPlayURL=function(b){var a;c.hasHTML5&&(a=J(b));return!x||a?a:b?b.match(c.filePattern)?!0:!1:null};this.canPlayLink=function(b){if(typeof b.type!=="undefined"&&b.type&&c.canPlayMIME(b.type))return!0;return c.canPlayURL(b.href)};
this.getSoundById=function(b){if(!b)throw Error("soundManager.getSoundById(): sID is null/undefined");return c.sounds[b]};this.onready=function(c,a){if(c&&c instanceof Function)return a||(a=h),aa("onready",c,a),u(),!0;else throw w("needFunction","onready");};this.ontimeout=function(c,a){if(c&&c instanceof Function)return a||(a=h),aa("ontimeout",c,a),u({type:"ontimeout"}),!0;else throw w("needFunction","ontimeout");};this.getMoviePercent=function(){return c.o&&typeof c.o.PercentLoaded!=="undefined"?
c.o.PercentLoaded():null};this._wD=this._writeDebug=function(){return!0};this._debug=function(){};this.reboot=function(){var b,a;for(b=c.soundIDs.length;b--;)c.sounds[c.soundIDs[b]].destruct();try{if(q)ga=c.o.innerHTML;I=c.o.parentNode.removeChild(c.o)}catch(e){}ga=I=null;c.enabled=m=U=ja=E=F=t=c.swfLoaded=!1;c.soundIDs=c.sounds=[];c.o=null;for(b in r)if(r.hasOwnProperty(b))for(a=r[b].length;a--;)r[b][a].fired=!1;h.setTimeout(function(){c.beginDelayedInit()},20)};this.destruct=function(){c.disable(!0)};
this.beginDelayedInit=function(){qa=!0;A();setTimeout(sa,20);P()};this._html5_events={abort:i(function(){}),canplay:i(function(){this._t._onbufferchange(0);var c=!isNaN(this._t.position)?this._t.position/1E3:null;this._t._html5_canplay=!0;if(this._t.position&&this.currentTime!==c)try{this.currentTime=c}catch(a){}}),load:i(function(){this._t.loaded||(this._t._onbufferchange(0),this._t._whileloading(this._t.bytesTotal,this._t.bytesTotal,this._t._get_html5_duration()),this._t._onload(!0))}),emptied:i(function(){}),
ended:i(function(){this._t._onfinish()}),error:i(function(){this._t._onload(!1)}),loadeddata:i(function(){}),loadedmetadata:i(function(){}),loadstart:i(function(){this._t._onbufferchange(1)}),play:i(function(){this._t._onbufferchange(0)}),playing:i(function(){this._t._onbufferchange(0)}),progress:i(function(b){if(this._t.loaded)return!1;var a,e=0,f=b.type==="progress",d=b.target.buffered;a=b.loaded||0;var oa=b.total||1;if(d&&d.length){for(a=d.length;a--;)e=d.end(a)-d.start(a);a=e/b.target.duration;
f&&isNaN(a)}isNaN(a)||(this._t._onbufferchange(0),this._t._whileloading(a,oa,this._t._get_html5_duration()),a&&oa&&a===oa&&c._html5_events.load.call(this,b))}),ratechange:i(function(){}),suspend:i(function(b){c._html5_events.progress.call(this,b)}),stalled:i(function(){}),timeupdate:i(function(){this._t._onTimer()}),waiting:i(function(){this._t._onbufferchange(1)})};Z=function(b){var a=this,e,f,d;this.sID=b.id;this.url=b.url;this._iO=this.instanceOptions=this.options=o(b);this.pan=this.options.pan;
this.volume=this.options.volume;this._lastURL=null;this.isHTML5=!1;this._a=null;this.id3={};this._debug=function(){};this._debug();this.load=function(b){var d=null;if(typeof b!=="undefined")a._iO=o(b,a.options),a.instanceOptions=a._iO;else if(b=a.options,a._iO=b,a.instanceOptions=a._iO,a._lastURL&&a._lastURL!==a.url)a._iO.url=a.url,a.url=null;if(!a._iO.url)a._iO.url=a.url;if(a._iO.url===a.url&&a.readyState!==0&&a.readyState!==2)return a;a._lastURL=a.url;a.loaded=!1;a.readyState=1;a.playState=0;if(V(a._iO)){if(d=
a._setup_html5(a._iO),!d._called_load)d.load(),d._called_load=!0,a._iO.autoPlay&&a.play()}else try{a.isHTML5=!1,a._iO=T(S(a._iO)),k===8?c.o._load(a.sID,a._iO.url,a._iO.stream,a._iO.autoPlay,a._iO.whileloading?1:0,a._iO.loops||1,a._iO.usePolicyFile):c.o._load(a.sID,a._iO.url,a._iO.stream?!0:!1,a._iO.autoPlay?!0:!1,a._iO.loops||1,a._iO.autoLoad?!0:!1,a._iO.usePolicyFile)}catch(e){fa()}return a};this.unload=function(){if(a.readyState!==0){if(a.isHTML5){if(f(),a._a)a._a.pause(),a._a.src=""}else k===8?
c.o._unload(a.sID,c.nullURL):c.o._unload(a.sID);e()}return a};this.destruct=function(b){if(a.isHTML5){if(f(),a._a)a._a.pause(),a._a.src="",K||a._remove_html5_events()}else a._iO.onfailure=null,c.o._destroySound(a.sID);b||c.destroySound(a.sID,!0)};this.start=this.play=function(b,W){var e,W=W===void 0?!0:W;b||(b={});a._iO=o(b,a._iO);a._iO=o(a._iO,a.options);a.instanceOptions=a._iO;if(a._iO.serverURL&&!a.connected)return a.getAutoPlay()||a.setAutoPlay(!0),a;V(a._iO)&&(a._setup_html5(a._iO),d());if(a.playState===
1&&!a.paused)if(e=a._iO.multiShot)a.isHTML5&&a.setPosition(a._iO.position);else return a;if(!a.loaded)if(a.readyState===0){if(!a.isHTML5)a._iO.autoPlay=!0;a.load(a._iO)}else if(a.readyState===2)return a;if(a.paused&&a.position&&a.position>0)a.resume();else{a.playState=1;a.paused=!1;(!a.instanceCount||a._iO.multiShotEvents||k>8&&!a.isHTML5&&!a.getAutoPlay())&&a.instanceCount++;a.position=typeof a._iO.position!=="undefined"&&!isNaN(a._iO.position)?a._iO.position:0;if(!a.isHTML5)a._iO=T(S(a._iO));if(a._iO.onplay&&
W)a._iO.onplay.apply(a),a._onplay_called=!0;a.setVolume(a._iO.volume,!0);a.setPan(a._iO.pan,!0);a.isHTML5?(d(),a._setup_html5().play()):c.o._start(a.sID,a._iO.loops||1,k===9?a.position:a.position/1E3)}return a};this.stop=function(b){if(a.playState===1){a._onbufferchange(0);a.resetOnPosition(0);if(!a.isHTML5)a.playState=0;a.paused=!1;a._iO.onstop&&a._iO.onstop.apply(a);if(a.isHTML5){if(a._a)a.setPosition(0),a._a.pause(),a.playState=0,a._onTimer(),f(),a.unload()}else c.o._stop(a.sID,b),a._iO.serverURL&&
a.unload();a.instanceCount=0;a._iO={}}return a};this.setAutoPlay=function(b){a._iO.autoPlay=b;a.isHTML5?a._a&&b&&a.play():c.o._setAutoPlay(a.sID,b);b&&!a.instanceCount&&a.readyState===1&&a.instanceCount++};this.getAutoPlay=function(){return a._iO.autoPlay};this.setPosition=function(b){b===void 0&&(b=0);var d=a.isHTML5?Math.max(b,0):Math.min(a.duration||a._iO.duration,Math.max(b,0));a.position=d;b=a.position/1E3;a.resetOnPosition(a.position);a._iO.position=d;if(a.isHTML5){if(a._a&&a._html5_canplay&&
a._a.currentTime!==b)try{a._a.currentTime=b}catch(e){}}else b=k===9?a.position:b,a.readyState&&a.readyState!==2&&c.o._setPosition(a.sID,b,a.paused||!a.playState);a.isHTML5&&a.paused&&a._onTimer(!0);return a};this.pause=function(b){if(a.paused||a.playState===0&&a.readyState!==1)return a;a.paused=!0;a.isHTML5?(a._setup_html5().pause(),f()):(b||b===void 0)&&c.o._pause(a.sID);a._iO.onpause&&a._iO.onpause.apply(a);return a};this.resume=function(){if(!a.paused)return a;a.paused=!1;a.playState=1;a.isHTML5?
(a._setup_html5().play(),d()):(a._iO.isMovieStar&&a.setPosition(a.position),c.o._pause(a.sID));!a._onplay_called&&a._iO.onplay?(a._iO.onplay.apply(a),a._onplay_called=!0):a._iO.onresume&&a._iO.onresume.apply(a);return a};this.togglePause=function(){if(a.playState===0)return a.play({position:k===9&&!a.isHTML5?a.position:a.position/1E3}),a;a.paused?a.resume():a.pause();return a};this.setPan=function(b,d){typeof b==="undefined"&&(b=0);typeof d==="undefined"&&(d=!1);a.isHTML5||c.o._setPan(a.sID,b);a._iO.pan=
b;if(!d)a.pan=b,a.options.pan=b;return a};this.setVolume=function(b,d){typeof b==="undefined"&&(b=100);typeof d==="undefined"&&(d=!1);if(a.isHTML5){if(a._a)a._a.volume=Math.max(0,Math.min(1,b/100))}else c.o._setVolume(a.sID,c.muted&&!a.muted||a.muted?0:b);a._iO.volume=b;if(!d)a.volume=b,a.options.volume=b;return a};this.mute=function(){a.muted=!0;if(a.isHTML5){if(a._a)a._a.muted=!0}else c.o._setVolume(a.sID,0);return a};this.unmute=function(){a.muted=!1;var b=typeof a._iO.volume!=="undefined";if(a.isHTML5){if(a._a)a._a.muted=
!1}else c.o._setVolume(a.sID,b?a._iO.volume:a.options.volume);return a};this.toggleMute=function(){return a.muted?a.unmute():a.mute()};this.onposition=function(c,b,d){a._onPositionItems.push({position:c,method:b,scope:typeof d!=="undefined"?d:a,fired:!1});return a};this.processOnPosition=function(){var b,d;b=a._onPositionItems.length;if(!b||!a.playState||a._onPositionFired>=b)return!1;for(;b--;)if(d=a._onPositionItems[b],!d.fired&&a.position>=d.position)d.method.apply(d.scope,[d.position]),d.fired=
!0,c._onPositionFired++;return!0};this.resetOnPosition=function(b){var d,e;d=a._onPositionItems.length;if(!d)return!1;for(;d--;)if(e=a._onPositionItems[d],e.fired&&b<=e.position)e.fired=!1,c._onPositionFired--;return!0};this._onTimer=function(c){var b={};if(a._hasTimer||c)return a._a&&(c||(a.playState>0||a.readyState===1)&&!a.paused)?(a.duration=a._get_html5_duration(),a.durationEstimate=a.duration,c=a._a.currentTime?a._a.currentTime*1E3:0,a._whileplaying(c,b,b,b,b),!0):!1};this._get_html5_duration=
function(){var c=a._a?a._a.duration*1E3:a._iO?a._iO.duration:void 0;return c&&!isNaN(c)&&c!==Infinity?c:a._iO?a._iO.duration:null};d=function(){a.isHTML5&&wa(a)};f=function(){a.isHTML5&&xa(a)};e=function(){a._onPositionItems=[];a._onPositionFired=0;a._hasTimer=null;a._onplay_called=!1;a._a=null;a._html5_canplay=!1;a.bytesLoaded=null;a.bytesTotal=null;a.position=null;a.duration=a._iO&&a._iO.duration?a._iO.duration:null;a.durationEstimate=null;a.failures=0;a.loaded=!1;a.playState=0;a.paused=!1;a.readyState=
0;a.muted=!1;a.didBeforeFinish=!1;a.didJustBeforeFinish=!1;a.isBuffering=!1;a.instanceOptions={};a.instanceCount=0;a.peakData={left:0,right:0};a.waveformData={left:[],right:[]};a.eqData=[];a.eqData.left=[];a.eqData.right=[]};e();this._setup_html5=function(b){var b=o(a._iO,b),d=K?c._global_a:a._a;decodeURI(b.url);var f=d&&d._t?d._t.instanceOptions:null;if(d){if(d._t&&f.url===b.url&&(!a._lastURL||a._lastURL===f.url))return d;K&&d._t&&d._t.playState&&b.url!==f.url&&d._t.stop();e();d.src=b.url;a.url=
b.url;a._lastURL=b.url;d._called_load=!1}else if(d=new Audio(b.url),d._called_load=!1,K)c._global_a=d;a.isHTML5=!0;a._a=d;d._t=a;a._add_html5_events();d.loop=b.loops>1?"loop":"";b.autoLoad||b.autoPlay?(d.autobuffer="auto",d.preload="auto",a.load(),d._called_load=!0):(d.autobuffer=!1,d.preload="none");d.loop=b.loops>1?"loop":"";return d};this._add_html5_events=function(){if(a._a._added_events)return!1;var b;a._a._added_events=!0;for(b in c._html5_events)c._html5_events.hasOwnProperty(b)&&a._a&&a._a.addEventListener(b,
c._html5_events[b],!1);return!0};this._remove_html5_events=function(){a._a._added_events=!1;for(var b in c._html5_events)c._html5_events.hasOwnProperty(b)&&a._a&&a._a.removeEventListener(b,c._html5_events[b],!1)};this._whileloading=function(c,b,d,e){a.bytesLoaded=c;a.bytesTotal=b;a.duration=Math.floor(d);a.bufferLength=e;if(a._iO.isMovieStar)a.durationEstimate=a.duration;else if(a.durationEstimate=a._iO.duration?a.duration>a._iO.duration?a.duration:a._iO.duration:parseInt(a.bytesTotal/a.bytesLoaded*
a.duration,10),a.durationEstimate===void 0)a.durationEstimate=a.duration;a.readyState!==3&&a._iO.whileloading&&a._iO.whileloading.apply(a)};this._onid3=function(c,b){var d=[],e,f;e=0;for(f=c.length;e<f;e++)d[c[e]]=b[e];a.id3=o(a.id3,d);a._iO.onid3&&a._iO.onid3.apply(a)};this._whileplaying=function(b,d,e,f,g){if(isNaN(b)||b===null)return!1;a.playState===0&&b>0&&(b=0);a.position=b;a.processOnPosition();if(k>8&&!a.isHTML5){if(a._iO.usePeakData&&typeof d!=="undefined"&&d)a.peakData={left:d.leftPeak,right:d.rightPeak};
if(a._iO.useWaveformData&&typeof e!=="undefined"&&e)a.waveformData={left:e.split(","),right:f.split(",")};if(a._iO.useEQData&&typeof g!=="undefined"&&g&&g.leftEQ&&(b=g.leftEQ.split(","),a.eqData=b,a.eqData.left=b,typeof g.rightEQ!=="undefined"&&g.rightEQ))a.eqData.right=g.rightEQ.split(",")}a.playState===1&&(!a.isHTML5&&c.flashVersion===8&&!a.position&&a.isBuffering&&a._onbufferchange(0),a._iO.whileplaying&&a._iO.whileplaying.apply(a),(a.loaded||!a.loaded&&a._iO.isMovieStar)&&a._iO.onbeforefinish&&
a._iO.onbeforefinishtime&&!a.didBeforeFinish&&a.duration-a.position<=a._iO.onbeforefinishtime&&a._onbeforefinish());return!0};this._onconnect=function(b){b=b===1;if(a.connected=b)a.failures=0,j(a.sID)&&(a.getAutoPlay()?a.play(void 0,a.getAutoPlay()):a._iO.autoLoad&&a.load()),a._iO.onconnect&&a._iO.onconnect.apply(a,[b])};this._onload=function(b){b=b?!0:!1;a.loaded=b;a.readyState=b?3:2;a._onbufferchange(0);a._iO.onload&&a._iO.onload.apply(a,[b]);return!0};this._onfailure=function(b,c,d){a.failures++;
if(a._iO.onfailure&&a.failures===1)a._iO.onfailure(a,b,c,d)};this._onbeforefinish=function(){if(!a.didBeforeFinish)a.didBeforeFinish=!0,a._iO.onbeforefinish&&a._iO.onbeforefinish.apply(a)};this._onjustbeforefinish=function(){if(!a.didJustBeforeFinish)a.didJustBeforeFinish=!0,a._iO.onjustbeforefinish&&a._iO.onjustbeforefinish.apply(a)};this._onfinish=function(){var b=a._iO.onfinish;a._onbufferchange(0);a.resetOnPosition(0);a._iO.onbeforefinishcomplete&&a._iO.onbeforefinishcomplete.apply(a);a.didBeforeFinish=
!1;a.didJustBeforeFinish=!1;if(a.instanceCount){a.instanceCount--;if(!a.instanceCount)a.playState=0,a.paused=!1,a.instanceCount=0,a.instanceOptions={},a._iO={},f();(!a.instanceCount||a._iO.multiShotEvents)&&b&&b.apply(a)}};this._onbufferchange=function(b){if(a.playState===0)return!1;if(b&&a.isBuffering||!b&&!a.isBuffering)return!1;a.isBuffering=b===1;a._iO.onbufferchange&&a._iO.onbufferchange.apply(a);return!0};this._ondataerror=function(){a.playState>0&&a._iO.ondataerror&&a._iO.ondataerror.apply(a)}};
ea=function(){return g.body?g.body:g._docElement?g.documentElement:g.getElementsByTagName("div")[0]};y=function(b){return g.getElementById(b)};o=function(b,a){var e={},f,d;for(f in b)b.hasOwnProperty(f)&&(e[f]=b[f]);f=typeof a==="undefined"?c.defaultOptions:a;for(d in f)f.hasOwnProperty(d)&&typeof e[d]==="undefined"&&(e[d]=f[d]);return e};l=function(){function b(a){var a=Da.call(a),b=a.length;c?(a[1]="on"+a[1],b>3&&a.pop()):b===3&&a.push(!1);return a}function a(a,b){var g=a.shift(),h=[f[b]];if(c)g[h](a[0],
a[1]);else g[h].apply(g,a)}var c=h.attachEvent,f={add:c?"attachEvent":"addEventListener",remove:c?"detachEvent":"removeEventListener"};return{add:function(){a(b(arguments),"add")},remove:function(){a(b(arguments),"remove")}}}();V=function(b){return!b.serverURL&&(b.type?J({type:b.type}):J(b.url)||p)};J=function(b){if(!c.useHTML5Audio||!c.hasHTML5)return!1;var a,e=c.audioFormats;if(!s){s=[];for(a in e)e.hasOwnProperty(a)&&(s.push(a),e[a].related&&(s=s.concat(e[a].related)));s=RegExp("\\.("+s.join("|")+
")","i")}a=typeof b.type!=="undefined"?b.type:null;b=typeof b==="string"?b.toLowerCase().match(s):null;if(!b||!b.length)if(a)b=a.indexOf(";"),b=(b!==-1?a.substr(0,b):a).substr(6);else return!1;else b=b[0].substr(1);if(b&&typeof c.html5[b]!=="undefined")return c.html5[b];else{if(!a)if(b&&c.html5[b])return c.html5[b];else a="audio/"+b;a=c.html5.canPlayType(a);return c.html5[b]=a}};za=function(){function b(b){var d,e,f=!1;if(!a||typeof a.canPlayType!=="function")return!1;if(b instanceof Array){d=0;for(e=
b.length;d<e&&!f;d++)if(c.html5[b[d]]||a.canPlayType(b[d]).match(c.html5Test))f=!0,c.html5[b[d]]=!0;return f}else return(b=a&&typeof a.canPlayType==="function"?a.canPlayType(b):!1)&&(b.match(c.html5Test)?!0:!1)}if(!c.useHTML5Audio||typeof Audio==="undefined")return!1;var a=typeof Audio!=="undefined"?Ga?new Audio(null):new Audio:null,e,f={},d,g;C();d=c.audioFormats;for(e in d)if(d.hasOwnProperty(e)&&(f[e]=b(d[e].type),d[e]&&d[e].related))for(g=d[e].related.length;g--;)c.html5[d[e].related[g]]=f[e];
f.canPlayType=a?b:null;c.html5=o(c.html5,f);return!0};w=function(){};S=function(b){if(k===8&&b.loops>1&&b.stream)b.stream=!1;return b};T=function(b){if(b&&!b.usePolicyFile&&(b.onid3||b.usePeakData||b.useWaveformData||b.useEQData))b.usePolicyFile=!0;return b};ia=function(b){typeof console!=="undefined"&&typeof console.warn!=="undefined"&&console.warn(b)};$=function(){return!1};ua=function(b){for(var a in b)b.hasOwnProperty(a)&&typeof b[a]==="function"&&(b[a]=$)};R=function(b){typeof b==="undefined"&&
(b=!1);(t||b)&&c.disable(b)};va=function(b){var a=null;if(b)if(b.match(/\.swf(\?.*)?$/i)){if(a=b.substr(b.toLowerCase().lastIndexOf(".swf?")+4))return b}else b.lastIndexOf("/")!==b.length-1&&(b+="/");return(b&&b.lastIndexOf("/")!==-1?b.substr(0,b.lastIndexOf("/")+1):"./")+c.movieURL};ca=function(){if(k!==8&&k!==9)c.flashVersion=8;var b=c.debugMode||c.debugFlash?"_debug.swf":".swf";if(c.useHTML5Audio&&!p&&c.audioFormats.mp4.required&&c.flashVersion<9)c.flashVersion=9;k=c.flashVersion;c.version=c.versionNumber+
(p?" (HTML5-only mode)":k===9?" (AS3/Flash 9)":" (AS2/Flash 8)");if(k>8)c.defaultOptions=o(c.defaultOptions,c.flash9Options),c.features.buffering=!0;k>8&&c.useMovieStar?(c.defaultOptions=o(c.defaultOptions,c.movieStarOptions),c.filePatterns.flash9=RegExp("\\.(mp3|"+c.netStreamTypes.join("|")+")(\\?.*)?$","i"),c.mimePattern=c.netStreamMimeTypes,c.features.movieStar=!0):(c.useMovieStar=!1,c.features.movieStar=!1);c.filePattern=c.filePatterns[k!==8?"flash9":"flash8"];c.movieURL=(k===8?"soundmanager2.swf":
"soundmanager2_flash9.swf").replace(".swf",b);c.features.peakData=c.features.waveformData=c.features.eqData=k>8};ta=function(b,a){if(!c.o||!c.allowPolling)return!1;c.o._setPolling(b,a)};Q=function(b,a){var e=a?a:c.url,f=c.altURL?c.altURL:e,d;d=ea();var h,k,i=B(),j,l=null,l=(l=g.getElementsByTagName("html")[0])&&l.dir&&l.dir.match(/rtl/i),b=typeof b==="undefined"?c.id:b;if(E&&F)return!1;if(p)return ca(),c.oMC=y(c.movieID),O(),F=E=!0,!1;E=!0;ca();c.url=va(c._overHTTP?e:f);a=c.url;c.wmode=!c.wmode&&
c.useHighPerformance&&!c.useMovieStar?"transparent":c.wmode;if(c.wmode!==null&&(n.match(/msie 8/i)||!q&&!c.useHighPerformance)&&navigator.platform.match(/win32|win64/i))c.specialWmodeCase=!0,c.wmode=null;d={name:b,id:b,src:a,width:"100%",height:"100%",quality:"high",allowScriptAccess:c.allowScriptAccess,bgcolor:c.bgColor,pluginspage:c._http+"//www.macromedia.com/go/getflashplayer",type:"application/x-shockwave-flash",wmode:c.wmode,hasPriority:"true"};if(c.debugFlash)d.FlashVars="debug=1";c.wmode||
delete d.wmode;if(q)e=g.createElement("div"),k='<object id="'+b+'" data="'+a+'" type="'+d.type+'" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="'+c._http+'//download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" width="'+d.width+'" height="'+d.height+'"><param name="movie" value="'+a+'" /><param name="AllowScriptAccess" value="'+c.allowScriptAccess+'" /><param name="quality" value="'+d.quality+'" />'+(c.wmode?'<param name="wmode" value="'+c.wmode+'" /> ':"")+
'<param name="bgcolor" value="'+c.bgColor+'" />'+(c.debugFlash?'<param name="FlashVars" value="'+d.FlashVars+'" />':"")+"</object>";else for(h in e=g.createElement("embed"),d)d.hasOwnProperty(h)&&e.setAttribute(h,d[h]);pa();i=B();if(d=ea())if(c.oMC=y(c.movieID)?y(c.movieID):g.createElement("div"),c.oMC.id){j=c.oMC.className;c.oMC.className=(j?j+" ":c.swfCSS.swfDefault)+(i?" "+i:"");c.oMC.appendChild(e);if(q)h=c.oMC.appendChild(g.createElement("div")),h.className=c.swfCSS.swfBox,h.innerHTML=k;F=!0}else{c.oMC.id=
c.movieID;c.oMC.className=c.swfCSS.swfDefault+" "+i;h=i=null;if(!c.useFlashBlock)if(c.useHighPerformance)i={position:"fixed",width:"8px",height:"8px",bottom:"0px",left:"0px",overflow:"hidden"};else if(i={position:"absolute",width:"6px",height:"6px",top:"-9999px",left:"-9999px"},l)i.left=Math.abs(parseInt(i.left,10))+"px";if(Fa)c.oMC.style.zIndex=1E4;if(!c.debugFlash)for(j in i)i.hasOwnProperty(j)&&(c.oMC.style[j]=i[j]);try{q||c.oMC.appendChild(e);d.appendChild(c.oMC);if(q)h=c.oMC.appendChild(g.createElement("div")),
h.className=c.swfCSS.swfBox,h.innerHTML=k;F=!0}catch(m){throw Error(w("appXHTML"));}}return!0};j=this.getSoundById;H=function(){if(p)return Q(),!1;if(c.o)return!1;c.o=c.getMovie(c.id);if(!c.o)I?(q?c.oMC.innerHTML=ga:c.oMC.appendChild(I),I=null,E=!0):Q(c.id,c.url),c.o=c.getMovie(c.id);c.oninitmovie instanceof Function&&setTimeout(c.oninitmovie,1);return!0};ba=function(b){if(b)c.url=b;H()};P=function(){setTimeout(ra,500)};ra=function(){if(U)return!1;U=!0;l.remove(h,"load",P);if(D&&!na)return!1;var b;
m||(b=c.getMoviePercent());setTimeout(function(){b=c.getMoviePercent();!m&&Ca&&(b===null?c.useFlashBlock||c.flashLoadTimeout===0?c.useFlashBlock&&ha():R(!0):c.flashLoadTimeout!==0&&R(!0))},c.flashLoadTimeout)};ba=function(b){if(b)c.url=b;H()};B=function(){var b=[];c.debugMode&&b.push(c.swfCSS.sm2Debug);c.debugFlash&&b.push(c.swfCSS.flashDebug);c.useHighPerformance&&b.push(c.swfCSS.highPerf);return b.join(" ")};ha=function(){w("fbHandler");var b=c.getMoviePercent(),a=c.swfCSS;if(c.ok()){if(c.oMC)c.oMC.className=
[B(),a.swfDefault,a.swfLoaded+(c.didFlashBlock?" "+a.swfUnblocked:"")].join(" ")}else{if(x)c.oMC.className=B()+" "+a.swfDefault+" "+(b===null?a.swfTimedout:a.swfError);c.didFlashBlock=!0;u({type:"ontimeout",ignoreInit:!0});c.onerror instanceof Function&&c.onerror.apply(h)}};v=function(){function b(){l.remove(h,"focus",v);l.remove(h,"load",v)}if(na||!D)return b(),!0;na=Ca=!0;L&&D&&l.remove(h,"mousemove",v);U=!1;b();return!0};G=function(b){if(m)return!1;if(p)return m=!0,u(),z(),!0;c.useFlashBlock&&
c.flashLoadTimeout&&!c.getMoviePercent()||(m=!0);if(t||b){if(c.useFlashBlock)c.oMC.className=B()+" "+(c.getMoviePercent()===null?c.swfCSS.swfTimedout:c.swfCSS.swfError);u({type:"ontimeout"});c.onerror instanceof Function&&c.onerror.apply(h);return!1}l.add(h,"unload",$);if(c.waitForWindowLoad&&!qa)return l.add(h,"load",z),!1;else z();return!0};aa=function(b,a,c){typeof r[b]==="undefined"&&(r[b]=[]);r[b].push({method:a,scope:c||null,fired:!1})};u=function(b){b||(b={type:"onready"});if(!m&&b&&!b.ignoreInit)return!1;
var a={success:b&&b.ignoreInit?c.ok():!t},e=b&&b.type?r[b.type]||[]:[],b=[],f,d=x&&c.useFlashBlock&&!c.ok();for(f=0;f<e.length;f++)e[f].fired!==!0&&b.push(e[f]);if(b.length){f=0;for(e=b.length;f<e;f++)if(b[f].scope?b[f].method.apply(b[f].scope,[a]):b[f].method(a),!d)b[f].fired=!0}return!0};z=function(){h.setTimeout(function(){c.useFlashBlock&&ha();u();c.onload instanceof Function&&c.onload.apply(h);c.waitForWindowLoad&&l.add(h,"load",z)},1)};C=function(){if(la!==void 0)return la;var b=!1,a=navigator,
c=a.plugins,f,d=h.ActiveXObject;if(c&&c.length)(a=a.mimeTypes)&&a["application/x-shockwave-flash"]&&a["application/x-shockwave-flash"].enabledPlugin&&a["application/x-shockwave-flash"].enabledPlugin.description&&(b=!0);else if(typeof d!=="undefined"){try{f=new d("ShockwaveFlash.ShockwaveFlash")}catch(g){}b=!!f}return la=b};ya=function(){var b,a;if(n.match(/iphone os (1|2|3_0|3_1)/i)){c.hasHTML5=!1;p=!0;if(c.oMC)c.oMC.style.display="none";return!1}if(c.useHTML5Audio){if(!c.html5||!c.html5.canPlayType)return c.hasHTML5=
!1,!0;else c.hasHTML5=!0;if(ma&&C())return!0}else return!0;for(a in c.audioFormats)c.audioFormats.hasOwnProperty(a)&&c.audioFormats[a].required&&!c.html5.canPlayType(c.audioFormats[a].type)&&(b=!0);c.ignoreFlash&&(b=!1);p=c.useHTML5Audio&&c.hasHTML5&&!b&&!c.requireFlash;return C()&&b};O=function(){var b,a=[];if(m)return!1;if(c.hasHTML5)for(b in c.audioFormats)c.audioFormats.hasOwnProperty(b)&&a.push(b+": "+c.html5[b]);if(p){if(!m)l.remove(h,"load",c.beginDelayedInit),c.enabled=!0,G();return!0}H();
try{c.o._externalInterfaceTest(!1),c.allowPolling&&ta(!0,c.flashPollingInterval?c.flashPollingInterval:c.useFastPolling?10:50),c.debugMode||c.o._disableDebug(),c.enabled=!0}catch(e){return R(!0),G(),!1}G();l.remove(h,"load",c.beginDelayedInit);return!0};sa=function(){if(ja)return!1;Q();H();return ja=!0};A=function(){if(da)return!1;da=!0;pa();if(!c.useHTML5Audio&&!C())c.useHTML5Audio=!0;za();c.html5.usingFlash=ya();x=c.html5.usingFlash;da=!0;g.removeEventListener&&g.removeEventListener("DOMContentLoaded",
A,!1);ba();return!0};wa=function(b){if(!b._hasTimer)b._hasTimer=!0};xa=function(b){if(b._hasTimer)b._hasTimer=!1};fa=function(){if(c.onerror instanceof Function)c.onerror();c.disable()};Aa=function(){if(!ma||!C())return!1;var b=c.audioFormats,a,e;for(e in b)if(b.hasOwnProperty(e)&&(e==="mp3"||e==="mp4"))if(c.html5[e]=!1,b[e]&&b[e].related)for(a=b[e].related.length;a--;)c.html5[b[e].related[a]]=!1};this._setSandboxType=function(){};this._externalInterfaceOK=function(){if(c.swfLoaded)return!1;(new Date).getTime();
c.swfLoaded=!0;D=!1;ma&&Aa();q?setTimeout(O,100):O()};ka=function(){g.readyState==="complete"&&(A(),g.detachEvent("onreadystatechange",ka));return!0};if(!c.hasHTML5||x)l.add(h,"focus",v),l.add(h,"load",v),l.add(h,"load",P),L&&D&&l.add(h,"mousemove",v);g.addEventListener?g.addEventListener("DOMContentLoaded",A,!1):g.attachEvent?g.attachEvent("onreadystatechange",ka):fa();g.readyState==="complete"&&setTimeout(A,100)}var X=null;if(typeof SM2_DEFER==="undefined"||!SM2_DEFER)X=new M;Y.SoundManager=M;Y.soundManager=
X})(window);