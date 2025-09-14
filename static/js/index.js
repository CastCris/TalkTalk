const BOX_DATA_UPDATE_ID = 'data_update';
const BOX_DATA_ID = 'data';

const BOX_MESSAGE_ID = 'message';
const BOX_MESSAGE_CONTENT_ID = 'message_content';
const BOX_MESSAGE_TIME_ID = 'message_time';
const BOX_MESSAGE_USER_ID = 'message_user';

const BOX_ROOM_BUTTON_ID = 'room_name_';

const BOX_ROOM_SELECTED = 'room_selected';
const BOX_ROOM_UNSELECTED = 'room_unselected';


const ROOM_DOM = (room_name, room_class) => {
    return `
        <li>
            <button onclick='room_change_button(this)'
            id='${BOX_ROOM_BUTTON_ID}${room_name}'>
            <p class='${room_class}'>${room_name}</p>
            </button>
        </li>`;
}

const MESSAGE_DOM = (message_content, message_data, user_name) => {
    const clock = time_now(message_data*1000)

    return `
        <div id="${BOX_MESSAGE_ID}">
            <p id="${BOX_MESSAGE_CONTENT_ID}">${message_content}</p>
            <span id="${BOX_MESSAGE_TIME_ID}">${clock["hours"]}:${clock["minutes"]}:${clock["seconds"]}</span>
            <span>--</span>
            <span id="${BOX_MESSAGE_USER_ID}">${user_name}</span>
        </div>
        <br>
    `
}

//
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
const OUTPUT_BOX = document.getElementById("chat_message");
const INPUT_BOX = document.getElementById("chat_input");
const FORMS = document.getElementById("chat_forms");

const ROOMS_ABLE = document.getElementById("rooms_able");

let clock_last = null;

//
function time_now(timestamp){
    const now = new Date(timestamp);
    now.toString();

    const seconds = String(now.getSeconds()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');

    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth()+1).padStart(2, '0');
    const year = now.getFullYear();

    const date_now = {
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,

        "day": day,
        "month": month,
        "year": year
    }

    return date_now;
}

function time_label_gen(time_past, time_future){
    if(!time_future)
        return null;
    if(time_future["day"] == time_past["day"] && time_future["month"] == time_past["month"] && time_future["year"] == time_past["year"])
        return null;
    // console.log(time_past);
    // console.log(time_future);

    return ` 
    <div id="${BOX_DATA_UPDATE_ID}">
        <h2 id="${BOX_DATA_ID}">${time_past["day"]}/${time_past["month"]}/${time_past["year"]}</h2>
    </div>
    ` 
}

//
function room_switch(room_name_old, room_name_new){
    socket.auth.serverRoom = room_name_new;
    socket.auth.messageOldOffset = 0;

    clock_last = null;
    sessionStorage.setItem('clockLast', null);

    socket.emit('room_change',{
        "room_name_old": room_name_old,
        "room_name_new": room_name_new
    });
    
    sessionStorage.setItem('serverRoom', room_name_new);
}

function room_change_type(room_name, room_type_new){
    const room_button = document.getElementById(BOX_ROOM_BUTTON_ID+room_name);
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
    const clock = time_now(message_offset*1000);

    const message_new = MESSAGE_DOM(message, message_offset, user_name);

    if(!clock_last || clock["day"] != clock_last["day"] || clock["month"] != clock_last["month"] || clock["year"] != clock_last["year"])
        clock_last = clock;

    sessionStorage.setItem('clockLast', JSON.stringify(clock_last))
    // sessionStorage.setItem('messageOffset', socket.auth.serverOffset);

    return message_new;
}

function message_show_begin(data){
    const message_offset = data["message_offset"];

    const clock = time_now(message_offset*1000);
    const clock_label = time_label_gen(clock, clock_last);

    const message_new = message_show_background(data);

    OUTPUT_BOX.innerHTML = message_new + OUTPUT_BOX.innerHTML;
    if(clock_label)
        OUTPUT_BOX.innerHTML = clock_label + OUTPUT_BOX.innerHTML;

}

function message_show_end(data){
    const message_offset = data["message_offset"];

    const clock = time_now(message_offset*1000);
    const clock_label = time_label_gen(clock, clock_last);

    const message_new = message_show_background(data);

    if(clock_label)
        OUTPUT_BOX.innerHTML += clock_label

    OUTPUT_BOX.innerHTML += message_new;
}

//
socket.on('connect', () => {
    clock_last = JSON.parse(sessionStorage.getItem('clockLast'));
});

// 
socket.on('message', (data) => {
    message_show_begin(data);

    socket.auth.messageNewOffset = data["message_offset"];
});

socket.on('message_recovery', (data) => {
    const message_scrolloff = data["scroll_off"];
    const message_compress = data["messages"];
    const message_decompress = pako.inflate(message_compress, { to: 'string' });

    const messages = JSON.parse(message_decompress);

    if(!message_scrolloff)
        return;

    console.log(data);
    console.log(messages);

    for(var i=0; i<messages.length; ++i){
        const message = messages[i];

        message_show_end(message);
    }

    socket.auth.messageOldOffset = messages[message_scrolloff-1]["message_offset"];
});

socket.on('output_clean', () => {
    OUTPUT_BOX.innerHTML = '';
});

socket.on('output_room_clean', () => {
    ROOMS_ABLE.innerHTML = '';
});

socket.on('room_recovery', (data) => {
    ROOMS_ABLE.innerHTML = '';

    const rooms = data["rooms"];
    for(var i=0;i<rooms.length;++i){
        const room_name = rooms[i];

        const room_new = ROOM_DOM(room_name, BOX_ROOM_UNSELECTED);
        ROOMS_ABLE.innerHTML += room_new;

        console.log(rooms[i]);
    }
});

socket.on('room_joined', (data) => {
    const room_name = data["room"];
    room_change_type(room_name, BOX_ROOM_SELECTED);
});

socket.on('room_leaved', (data) => {
    const room_name = data["room"];
    room_change_type(room_name, BOX_ROOM_UNSELECTED);
});

socket.on('room_create', (data) => {
    ROOMS_ABLE.innerHTML = '';

    const rooms = data["room_able"]
    for(var i=0;i<rooms.length;++i){
        const room_name = rooms[i];

        let room_class = BOX_ROOM_UNSELECTED;
        if(room_name == socket.auth.serverRoom)
            room_class = BOX_ROOM_SELECTED;

        const room_new = ROOM_DOM(room_name, room_class)
        
        ROOMS_ABLE.innerHTML += room_new;
    }
});


socket.on('user_invalid', () => {
    console.log('AAAAAA');
    OUTPUT_BOX.innerHTML = '<p>Hey! Looks that you are using a invalid user name, for some reason. Please, sign with other account or create a new</p>';
})


//
FORMS.addEventListener('submit', (e) => {
    e.preventDefault();

    if(!INPUT_BOX.value)
        return;
    socket.emit('message', {
        "message_content": INPUT_BOX.value,
        "message_id": socket_id+'-'+socket_id_counter,
        "room": socket.auth.serverRoom
    });

    INPUT_BOX.value='';
    ++socket_id_counter;
});

OUTPUT_BOX.addEventListener('scroll', () => {
    if(OUTPUT_BOX.scrollHeight - OUTPUT_BOX.scrollTop == OUTPUT_BOX.clientHeight){
        console.log('AAAA');
        socket.emit('message_load', socket.auth);
    }
});

function room_change_button(button){
    const room_name_new = button.id.split(BOX_ROOM_BUTTON_ID)[1]
    const room_name_old = socket.auth.serverRoom;
    
    room_switch(room_name_old, room_name_new);
}
