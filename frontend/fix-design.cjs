const fs = require('fs');
const path = require('path');

function walkSync(dir, callback) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const p = path.join(dir, file);
    if (fs.statSync(p).isDirectory()) walkSync(p, callback);
    else callback(p);
  }
}

walkSync(path.join(process.cwd(), 'src'), (filePath) => {
  if (!filePath.endsWith('.vue') && !filePath.endsWith('.css')) return;
  let content = fs.readFileSync(filePath, 'utf8');
  let original = content;

  content = content.replace(/\bbg-white\b/g, 'bg-surface-bright');
  content = content.replace(/\btext-white\b/g, 'text-on-primary');
  
  content = content.replace(/\b([mp])l-([a-z0-9\/]+)\b/g, '$1s-$2');
  content = content.replace(/\b([mp])r-([a-z0-9\/]+)\b/g, '$1e-$2');
  content = content.replace(/\b-([mp])l-([a-z0-9\/]+)\b/g, '-$1s-$2');
  content = content.replace(/\b-([mp])r-([a-z0-9\/]+)\b/g, '-$1e-$2');
  
  content = content.replace(/\bleft-([a-z0-9\/]+)\b/g, 'start-$1');
  content = content.replace(/\b-left-([a-z0-9\/]+)\b/g, '-start-$1');
  content = content.replace(/\bright-([a-z0-9\/]+)\b/g, 'end-$1');
  content = content.replace(/\b-right-([a-z0-9\/]+)\b/g, '-end-$1');

  // css physical props
  content = content.replace(/padding-left:/g, 'padding-inline-start:');
  content = content.replace(/padding-right:/g, 'padding-inline-end:');
  content = content.replace(/margin-left:/g, 'margin-inline-start:');
  content = content.replace(/margin-right:/g, 'margin-inline-end:');
  content = content.replace(/\bwhite\b/g, '#faf9f6'); // targeted replacement for main.css

  // Fix margin/padding singletons overriding auto formatting
  content = content.replace(/([mp])[ls]-\$2/g, ''); // just a fail safe if corrupted, shouldn't hit

  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('Updated', filePath);
  }
});
