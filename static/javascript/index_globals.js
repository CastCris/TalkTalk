export const DOM_ROOM_ID = 'rooms';
export const DOM_ROOM_ABLE_ID = 'rooms_able';

export const DOM_INTERFACE_USER_MAIN_ID = 'interface_user_main';

export const DOM_CHAT_ID = 'chat';
export const DOM_CHAT_FORMS_ID = 'chat_forms';
export const DOM_CHAT_INPUT_ID = 'chat_input';
export const DOM_CHAT_MESSAGE_ID = 'chat_message';

export const DOM_SERVER_STATUS_ID = 'server_status';
export const DOM_SERVER_STATUS_PULL_ID = 'server_status_pull';

export const DOM_SERVER_STATUS_HIGHLIGHT_ID = 'server_status_highlight';
export const DOM_SERVER_STAUTS_HIGHLIGHT_NODE_ID = 'server_status_highlight_node';

export const DOM_SERVER_STATUS_RESULT_ID = 'server_status_result';

//
export const DOM_DATA_UPDATE_ID = 'data_update';
export const DOM_DATA_ID = 'data';

export const DOM_MESSAGE_ID = 'message';
export const DOM_MESSAGE_CONTENT_ID = 'message_content';
export const DOM_MESSAGE_TIME_ID = 'message_time';
export const DOM_MESSAGE_USER_ID = 'message_user';

export const DOM_BUTTON_MESSAGE_MORE = 'message_more';

export const DOM_BUTTON_ROOM_ID = 'room_name_';

export const DOM_ROOM_SELECTED = 'room_selected';
export const DOM_ROOM_UNSELECTED = 'room_unselected';

export const DOM_ROOM = (room_name, room_class) => {
    return `
        <li>
            <button onclick='room_change_button(this)'
            id='${DOM_BUTTON_ROOM_ID}${room_name}'>
            <p class='${room_class}'>${room_name}</p>
            </button>
        </li>`;
}

export const DOM_MESSAGE = (message_content, message_data, user_name) => {
    const clock = time_now(message_data*1000)

    return `
        <div id="${DOM_MESSAGE_ID}">
            <p id="${DOM_MESSAGE_CONTENT_ID}">${message_content}</p>
            <span id="${DOM_MESSAGE_TIME_ID}">${clock["hours"]}:${clock["minutes"]}:${clock["seconds"]}</span>
            <span>--</span>
            <span id="${DOM_MESSAGE_USER_ID}">${user_name}</span>
        </div>
        <br>
    `
}

export const DOM_MESSAGE_MORE = `
    <button id="${DOM_BUTTON_MESSAGE_MORE}" onclick='message_load()'>
        <h3>More</h3>
    </div>
`

export const DOM_SERVER_STATUS_HIGHTLIGHT = (highlight_name) => {
    return `
    <li>
        <button
        id="${DOM_SERVER_STATUS_ID}_${highlight_name}" 
        class="${DOM_SERVER_STAUTS_HIGHLIGHT_NODE_ID}"
        onclick='server_status_data_get(this)'>
        <h3>${highlight_name}</h3>
        </button>
    </li>`
}

export const DOM_SERVER_STATUS_NODE = (node_name, node_content) => {
    return `
    <div class="server_status_node_${node_name}">
        <p>${node_content}</p>
    </div>
    `
}

//
export function time_now(timestamp){
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

//
export const ROOM = document.getElementById(DOM_ROOM_ID);
export const ROOM_ABLE = document.getElementById(DOM_ROOM_ABLE_ID);

export const CHAT = document.getElementById(DOM_CHAT_ID);
export const CHAT_FORMS = document.getElementById(DOM_CHAT_FORMS_ID);
export const CHAT_INPUT = document.getElementById(DOM_CHAT_INPUT_ID);
export const CHAT_MESSAGE = document.getElementById(DOM_CHAT_MESSAGE_ID);

export const SERVER_STATUS = document.getElementById(DOM_SERVER_STATUS_ID);
export const SERVER_STATUS_PULL = document.getElementById(DOM_SERVER_STATUS_PULL_ID);

export const SERVER_STATUS_HIGHLIGHT = document.getElementById(DOM_SERVER_STATUS_HIGHLIGHT_ID);
export const SERVER_STATUS_RESULT = document.getElementById(DOM_SERVER_STATUS_RESULT_ID);
