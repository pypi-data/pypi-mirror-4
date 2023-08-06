function killUndefined(arr){
  return arr.map(function(item){
    if(typeof item != 'object')
      return item;
    var ret = {};
    for(var i in item){
      if(typeof item[i] != 'undefined')
        ret[i] = item[i];
    }
    return ret;
  });
}

function graft(parentNode, childNodes, parentLongname, parentName) {
    childNodes
    .filter(function (element) {
        return (element.memberof === parentLongname);
    })
    .forEach(function (element, index) {
      if(!(element.kind in parentNode))
        parentNode[element.kind] = [];

      var clone = {};
      var backlist = ['comment', 'meta', 'memberof'];
      for(var i in element){
        if((backlist.indexOf(i) == -1) && (typeof element[i] != 'function') && (typeof element[i] != 'undefined'))
          clone[i] = Array.isArray(element[i]) ? killUndefined(element[i]) :  element[i];
      }

      parentNode[element.kind].push(clone);
      graft(clone, childNodes, element.longname, element.name);

    });
}

exports.publish = function(data, opts) {
    // data.remove({undocumented: true});
    if (opts.destination === 'console') {
      data.remove({undocumented: true});
      var dock = {};
      graft(dock, data.get());
      console.log(dock);
    } else {
      console.log('This template only supports output to the console. Use the option "-d console" when you run JSDoc.');
      throw "UNIMPLEMENTED";
    }
};