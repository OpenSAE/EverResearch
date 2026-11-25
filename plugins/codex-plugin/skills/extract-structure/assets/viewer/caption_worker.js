/* Purpose and main function: to calculate the location of the connection in the back and to keep the canvas and the operating controls responsive.
 * Scope: ExtractStructure Current text layouts that can be shown in figure; old jobs cancelled by the caller when the canvassing switch.
 */
'use strict';
self.window=self;
importScripts('./inline_labels.js');
self.onmessage=({data})=>{
  try{
    const started=performance.now();
    const result=layoutInlineCaptionModel(data.model,data.segments,data.positions,data.extra,data.policy);
    self.postMessage({result,elapsedMs:performance.now()-started});
  }catch(error){self.postMessage({error:String(error.message||error)});}
};
