// Resolve authored target artifacts, with legacy generic-path fallback.
const fs=require('node:fs'),path=require('node:path');
module.exports=function artifactFile(run,target,logical){
  const metadata=JSON.parse(fs.readFileSync(path.join(run,'run.json'),'utf8'));
  if(!metadata.artifact_manifests)return logical;
  const manifestPath=metadata.artifact_manifests[target];
  if(typeof manifestPath!=='string'||manifestPath.includes('\\')||manifestPath.split('/').length!==2||manifestPath.split('/')[0]!==target||['.','..'].includes(manifestPath.split('/')[1]))throw new Error('Unsafe artifact manifest path');
  const manifest=JSON.parse(fs.readFileSync(path.join(run,manifestPath),'utf8'));
  if(manifest.schema!=='aptlantis.artifact-manifest.v2'||manifest.target!==target)throw new Error('Unexpected artifact manifest');
  const files=manifest.files.filter(file=>file.logical_name===logical);
  if(files.length!==1||/[\\/]/.test(files[0].file)||['.','..'].includes(files[0].file))throw new Error('Missing, duplicate or unsafe artifact: '+logical);
  return files[0].file;
};
