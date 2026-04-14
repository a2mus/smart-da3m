const fs = require('fs');
const glob = require('glob');

const files = glob.sync('frontend/src/**/*.vue');
let count = 0;
files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  const initial = content;
  
  // text-alignment
  content = content.replace(/\btext-left\b/g, 'text-start');
  content = content.replace(/\btext-right\b/g, 'text-end');
  
  // Borders
  content = content.replace(/\bborder-l\b/g, 'border-s');
  content = content.replace(/\bborder-r\b/g, 'border-e');
  content = content.replace(/\bborder-l-([a-z0-9]+)\b/g, 'border-s-$1');
  content = content.replace(/\bborder-r-([a-z0-9]+)\b/g, 'border-e-$1');
  
  // Border radius geometry (rounded-l, rounded-r, rounded-tl, etc.)
  content = content.replace(/\brounded-l\b/g, 'rounded-s');
  content = content.replace(/\brounded-r\b/g, 'rounded-e');
  content = content.replace(/\brounded-l-([a-z0-9]+)\b/g, 'rounded-s-$1');
  content = content.replace(/\brounded-r-([a-z0-9]+)\b/g, 'rounded-e-$1');
  
  content = content.replace(/\brounded-tl\b/g, 'rounded-ss');
  content = content.replace(/\brounded-tr\b/g, 'rounded-se');
  content = content.replace(/\brounded-bl\b/g, 'rounded-es');
  content = content.replace(/\brounded-br\b/g, 'rounded-ee');
  content = content.replace(/\brounded-tl-([a-z0-9]+)\b/g, 'rounded-ss-$1');
  content = content.replace(/\brounded-tr-([a-z0-9]+)\b/g, 'rounded-se-$1');
  content = content.replace(/\brounded-bl-([a-z0-9]+)\b/g, 'rounded-es-$1');
  content = content.replace(/\brounded-br-([a-z0-9]+)\b/g, 'rounded-ee-$1');
  
  if (initial !== content) {
    fs.writeFileSync(file, content, 'utf8');
    console.log('Fixed:', file);
    count++;
  }
});
console.log('Total fixed:', count);
