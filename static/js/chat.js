var chat_block = $('.chat-box')
var experiment = chat_block.data('experiment-pk')

var socket = new WebSocket('ws://'+ LabRepo.domain + '/chat/'  + experiment + '/');

socket.onopen = function() {
    debug_log("Connection is opened");
};

socket.onclose = function(event) {
    if (event.wasClean) {
        debug_log('Connection is closed');
    } else {
        debug_log('Disconnection');
    }
    debug_log('Code: ' + event.code + ' reason: ' + event.reason);
};

socket.onmessage = function(event) {
    debug_log('Get message: ', event.data)
    var data = JSON.parse(event.data);
    $('.comment-form').closest('.comment-area').find('.comments-block').append(data.html);
    comments_scroll_to_end()
};

socket.onerror = function(error) {
    debug_log("Error " + error.message);
}

function debug_log(){
    if(LabRepo.debug){
        console.log('[SOCKETS]', Array.prototype.slice.call(arguments).join(' '))
    }
}

function comments_scroll_to_end(a) {
    $(".comments-block").scrollTop($(".comments-block")[0].scrollHeight);
};
