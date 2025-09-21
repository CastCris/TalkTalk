import * as index from './index_globals.js';

const socket = io({
    auth:{
        messageNewOffset: 0,
        messageOldOffset: 0,
        serverRoom: [ sessionStorage.getItem('serverRoom') || 'index'][0],

        typeConnection: "room"
    }
});

const socket_id = crypto.getRandomValues(new Uint32Array(1))[0];
let socket_id_counter = 0;


//
function time_recent(time1, time2){
    const data1 = new Date(`${time1['year']}-${time1['month']}-${time1['day']}`);
    const data2 = new Date(`${time2['year']}-${time2['month']}-${time2['day']}`);

    if(isNaN(data2.getTime()))
        return 1;

    // console.log(data1.getTime(), data2.getTime());

    if(data1.getTime() > data2.getTime())
        return 1;
    return 0;
}


function time_label_gen(time_past, time_future){
    if(!time_future)
        return null;
    if(time_future["day"] == time_past["day"] && time_future["month"] == time_past["month"] && time_future["year"] == time_past["year"])
        return null;
    // console.log(time_past);
    // console.log(time_future);

    return ` 
    <div id="${index.DOM_DATA_UPDATE_ID}">
        <h2 id="${index.DOM_DATA_ID}">${time_past["day"]}/${time_past["month"]}/${time_past["year"]}</h2>
    </div>
    ` 
}

//
function room_switch(room_name_old, room_name_new){
    socket.auth.serverRoom = room_name_new;
    socket.auth.messageOldOffset = 0;

    sessionStorage.setItem('clockLast', 'null');

    socket.emit('room_change',{
        "room_name_old": room_name_old,
        "room_name_new": room_name_new
    });
    
    sessionStorage.setItem('serverRoom', room_name_new);
}

function room_change_type(room_name, room_type_new){
    const room_button = document.getElementById(index.DOM_BUTTON_ROOM_ID+room_name);
    const room_button_type = room_button.children[0];

    room_button_type.className = room_type_new;
}

//
function message_show_background(data){
    const message = data["message_content"];
    const message_offset = data["message_offset"];

    const user_name = data["message_user_name"];

    //
    // console.log(data);
    const clock = index.time_now(message_offset*1000);

    const message_new = index.DOM_MESSAGE(message, message_offset, user_name);
    // sessionStorage.setItem('messageOffset', socket.auth.serverOffset);

    return message_new;
}

function message_show_begin(data, clock_last, message_html){
    const message_offset = data["message_offset"];

    const clock = index.time_now(message_offset*1000);
    const clock_label = time_label_gen(clock, clock_last.clock);

    const message_new = message_show_background(data);

    if(clock_label){
        message_html.innerHTML = clock_label + message_html.innerHTML;
    }
    message_html.innerHTML = message_new + message_html.innerHTML;

    clock_last.clock = clock;
}

function message_show_end(data, clock_last, message_html){
    const message_offset = data["message_offset"];

    const clock = index.time_now(message_offset*1000);
    const clock_label = time_label_gen(clock, clock_last.clock);

    const message_new = message_show_background(data);

    if(clock_label){
        message_html.innerHTML += clock_label
    }

    message_html.innerHTML += message_new;

    clock_last.clock = clock;
}


//
socket.on('connect', () => {
    // sessionStorage.setItem('clockLast', 'null');
});

// 
socket.on('message', (data) => {
    // console.log(data);
    let clock_last = { clock: JSON.parse(sessionStorage.getItem('clockLast')) };
    const message_html = { innerHTML: '' };

    message_show_begin(data, clock_last, message_html);

    index.CHAT_MESSAGE.innerHTML = message_html.innerHTML + index.CHAT_MESSAGE.innerHTML;

    socket.auth.messageNewOffset = data["message_offset"];
    sessionStorage.setItem('clockLast', JSON.stringify(clock_last.clock));
});

socket.on('message_recovery', (data) => {
    const message_scrolloff = data["scroll_off"];
    const message_compress = data["messages"];
    const message_decompress = pako.inflate(message_compress, { to: 'string' });

    const messages = JSON.parse(message_decompress);

    if(!message_scrolloff)
        return;

    //
    const message_more = document.getElementById(index.DOM_BUTTON_MESSAGE_MORE);
    if(message_more)
        message_more.remove();

    //
    // console.log(data);
    console.log(messages);

    let clock_last = { clock: null };
    const message_html = { innerHTML: '' };
    for(var i=0; i<messages.length; ++i){
        const message = messages[i];

        message_show_end(message, clock_last, message_html);
    }

    index.CHAT_MESSAGE.innerHTML += message_html.innerHTML;
    index.CHAT_MESSAGE.innerHTML += index.DOM_MESSAGE_MORE ;

    //
    socket.auth.messageOldOffset = messages[message_scrolloff-1]["message_offset"];

    const clock = index.time_now(messages[0]["message_offset"]*1000);
    const clock_storage = sessionStorage.getItem('clockLast');

    if(!clock_storage || clock_storage == 'null')
        sessionStorage.setItem('clockLast', JSON.stringify(clock));
    else if(time_recent(clock, JSON.parse(clock_storage))){
        sessionStorage.setItem('clockLast', JSON.stringify(clock));
        // console.log('clock: ', sessionStorage);
    }

});


socket.on('output_clean', () => {
    index.CHAT_MESSAGE.innerHTML = '';
});

socket.on('output_room_clean', () => {
    index.ROOM_ABLE.innerHTML = '';
});


socket.on('room_recovery', (data) => {
    index.ROOM_ABLE.innerHTML = '';

    const rooms = data["rooms"];
    for(var i=0;i<rooms.length;++i){
        const room_name = rooms[i];

        const room_new = index.DOM_ROOM(room_name, index.DOM_ROOM_UNSELECTED);
        index.ROOM_ABLE.innerHTML += room_new;

        console.log(rooms[i]);
    }
});

socket.on('room_joined', (data) => {
    const room_name = data["room"];
    room_change_type(room_name, index.DOM_ROOM_SELECTED);
});

socket.on('room_leaved', (data) => {
    const room_name = data["room"];
    room_change_type(room_name, index.DOM_ROOM_UNSELECTED);
});

socket.on('room_create', (data) => {
    index.ROOM_ABLE.innerHTML = '';

    const rooms = data["room_able"]
    for(var i=0;i<rooms.length;++i){
        const room_name = rooms[i];

        let room_class = index.DOM_ROOM_UNSELECTED;
        if(room_name == socket.auth.serverRoom)
            room_class = index.DOM_ROOM_SELECTED;

        const room_new = index.DOM_ROOM(room_name, room_class)
        
        index.ROOM_ABLE.innerHTML += room_new;
    }
});


socket.on('user_invalid', () => {
    console.log('AAAAAA');
    index.CHAT_MESSAGE.innerHTML = '<p>Hey! Looks that you are using a invalid user name, for some reason. Please, sign with other account or create a new</p>';
})


socket.on('server_status_highlight', (data) => {
    const highlight = data["highlight"];
    let html_content = '';

    index.SERVER_STATUS_HIGHLIGHT.innerHTML = '';

    for(var i=0; i<highlight.length; ++i){
        const highlight_name = highlight[i];
        html_content += index.DOM_SERVER_STATUS_HIGHTLIGHT(highlight_name);
    }

    index.SERVER_STATUS_HIGHLIGHT.innerHTML += html_content;
});

socket.on('server_status_data', (data) => {
    console.log(data);

    const highlight_name = data["highlight"];
    const content = data["result"];

    const output_box = document.getElementById(index.DOM_SERVER_STATUS_RESULT_ID);
    output_box.innerHTML = '';

    let innerHTML = '';
    for(var i=0; i<content.length; ++i){
        innerHTML += index.DOM_SERVER_STATUS_NODE(highlight_name, content[i]);
    }

    output_box.innerHTML += innerHTML;
});

//
index.CHAT_FORMS.addEventListener('submit', (e) => {
    e.preventDefault();

    if(!index.CHAT_INPUT.value.length)
        return;
    socket.emit('message', {
        "message_content": index.CHAT_INPUT.value,
        "message_id": socket_id+'-'+socket_id_counter,
        "room": socket.auth.serverRoom
    });

    index.CHAT_INPUT.value='';
    ++socket_id_counter;
});

index.CHAT_MESSAGE.addEventListener('scroll', () => {
    if(index.CHAT_MESSAGE.scrollHeight - index.CHAT_MESSAGE.scrollTop == index.CHAT_MESSAGE.clientHeight){
        socket.emit('message_load', socket.auth);
    }
});

// Window function
function room_change_button(button){
    const room_name_new = button.id.split(index.DOM_BUTTON_ROOM_ID)[1]
    const room_name_old = socket.auth.serverRoom;
    
    room_switch(room_name_old, room_name_new);
}

function server_status_data_get(button){
    const highlight_name = button.id.split(index.DOM_SERVER_STATUS_ID+'_')[1];

    socket.emit('server_status_data_get', {
        "highlight_name": highlight_name
    });
}

function message_load(){
    const message_more = document.getElementById(index.DOM_BUTTON_MESSAGE_MORE);
    message_more.remove();

    socket.emit('message_load', socket.auth);
}


window.room_change_button = room_change_button;
window.server_status_data_get = server_status_data_get;
window.message_load = message_load;
