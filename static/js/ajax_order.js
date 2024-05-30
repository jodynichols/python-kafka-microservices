var log_data;
var log_data_autoscroll;
var order_id;
var status_topped;
var last_result = -1;
var one_last_call = 0;

$(document).ready(function () {
    log_data = $("#log_data");
    log_data_autoscroll = $("#log_data_autoscroll");
    order_id = $("#order_id").val();
    status_topped = $("#status_topped").val();
    get_logs();
    setTimeout(function () {
        update_order_status();
    }, 1000);
});

function toggle_status(remove, add) {
    $("#order_status").removeClass(remove);
    $("#order_status").addClass(add);
}

// Update view order every 2 secs (in a realistic scenario that would be better off using REACT)
function update_order_status() {
    if (order_id) {
        $.ajax({
            type: "PUT",
            async: true,
            url: "/orders/" + order_id,
            dataType: "json",
            success: function (data) {
                if (data) {
                    if (last_result != status_topped) {
                        $("#order_status").text(data.str);
                        setTimeout(function () {
                            update_order_status();
                        }, 2000);
                    }
                    if (data.status == status_topped) {
                        toggle_status("badge-info", "badge-success");
                    }
                    else if (last_result != data.status && last_result != -1) {
                        var timeout;
                        for (var i = 0; i < 3; i++) {
                            timeout = i * 500;
                            setTimeout(function () {
                                toggle_status("badge-info", "badge-warning");
                            }, timeout);
                            setTimeout(function () {
                                toggle_status("badge-warning", "badge-info");
                            }, 250 + timeout);
                        }
                    }
                    last_result = data.status;
                }
            }
        });
    }
}

// Update view order every 1 sec (in a realistic scenario that would be better off using REACT)
function get_logs() {
    if (order_id) {
        if (one_last_call == 0) {
            $.ajax({
                type: "PUT",
                async: true,
                url: "/logs/" + order_id,
                dataType: "json",
                success: function (data) {
                    if (data) {
                        if (data.all_logs != log_data.html()) {
                            log_data.html(data.all_logs);
                            if (log_data_autoscroll.prop("checked")) {
                                log_data.scrollTop(log_data[0].scrollHeight);
                            }
                        }
                        if (data.webapp) {
                            $("#webapp_data").html(data.webapp);
                        }
                        if (data.msvc_label) {
                            $("#msvc_label_data").html(data.msvc_label);
                        }
                        if (data.msvc_mix) {
                            $("#msvc_mix_data").html(data.msvc_mix);
                        }
                        if (data.msvc_topping) {
                            $("#msvc_top_data").html(data.msvc_top);
                        }
                        if (data.msvc_status) {
                            $("#msvc_status_data").html(data.msvc_status);
                        }
                        setTimeout(function () {
                            get_logs();
                        }, 1000);
                    }
                }
            });
        }
        if (last_result == status_topped) {
            one_last_call += 1;
        }
    }
}