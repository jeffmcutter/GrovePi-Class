Template.sensorTable.helpers({
    sensors: function() {
        return Sensors.find();
    },
});

Template.sensorRow.helpers({
    datetime: function() {
        return Date(Template.currentData().timestamp);
    }
});

UI.registerHelper("arrayify", function(obj){
    var result = [];
    var keys = [];
    for (var key in obj){
        keys.push(key);
    }
    for (var key in keys.sort()){
        result.push({name:keys[key],value:obj[keys[key]]});
    }
    return result;
});
