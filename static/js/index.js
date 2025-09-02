const socket = io('http://localhost:5000',{
    auth:{
        messageOffset: 0,
        serverRoom: 'index',
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

function label_time_add(time_curr, time_prev){
    if(!time_prev)
        return;
    if(time_curr["day"] == time_prev["day"] && time_curr["month"] == time_prev["month"] && time_curr["year"] == time_prev["year"])
        return;
    // console.log(time_prev);

    OUTPUT_BOX.innerHTML = ` 
    <div class="update_data">
        <p class="data">${time_prev["day"]}/${time_prev["month"]}/${time_prev["year"]}
    </div>
    ` + OUTPUT_BOX.innerHTML;
}


//
socket.on('connect', () => {
    clock_last = null;
});

socket.on('message', (data) => {
    const message = data["message_content"];
    const serverDataOffset = data["message_offset"];

    const user_name = data["user_name"];

    console.log(data);

    const clock = time_now(serverDataOffset*1000)
    label_time_add(clock, clock_last);

    OUTPUT_BOX.innerHTML = `
        <div class="message">
            <p class="message_content">${message}</p>
            <span class="message_time">${clock["hours"]}:${clock["minutes"]}:${clock["seconds"]}</span>
            <span>--</span>
            <span class="message_user">${user_name}</span>
        </div>
        <br>
    ` + OUTPUT_BOX.innerHTML;

    socket.auth.serverOffset = serverDataOffset
    clock_last = clock;
});

socket.on('room_recovery', (data) => {
    ROOMS_ABLE.innerHTML = '';

    rooms = data["rooms"];
    for(var i=0;i<rooms.length;++i){
        ROOMS_ABLE.innerHTML += `
            <li>
                <button onclick='room_change(this)' id='room_name_${rooms[i]}'> ${rooms[i]} </button>
            </li>`;
    }
});

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

function room_change(button){
    const room_name = button.id.split('room_name_')[1]

    OUTPUT_BOX.innerHTML = '';
    ROOMS_ABLE.innerHTML = '';
    
    socket.auth.serverRoom = room_name;


    socket.emit('room_change',{
        "room_name": room_name
    });
}
