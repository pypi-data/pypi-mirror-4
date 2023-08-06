// This contains template-specific javascript
//import jquery.js

function filter_log(threshold_level) {
    var log_levels = ["Debug", "Info", "Warning", "Error", "Fatal"]

   // assert(threshold_level in log_levels);
    var action = "hide";
    for (var idx = 0; idx < log_levels.length; idx++){
        var level = log_levels[idx];
        if (level === threshold_level){
            action = "show";
        }
        $('.log' + level)[action]();
    }
}
