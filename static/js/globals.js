const DOM_ROOM_ID = 'rooms';
const DOM_ROOM_ABLE_ID = 'rooms_able';

const DOM_INTERFACE_USER_MAIN_ID = 'interface_user_main';

const DOM_CHAT_ID = 'chat';
const DOM_CHAT_FORMS_ID = 'chat_forms';
const DOM_CHAT_INPUT_ID = 'chat_input';
const DOM_CHAT_MESSAGE_ID = 'chat_message';

const DOM_SERVER_STATUS_ID = 'server_status';
const DOM_SERVER_STATUS_PULL_ID = 'button_pull';

//
const DOM_DATA_UPDATE_ID = 'data_update';
const DOM_DATA_ID = 'data';

const DOM_MESSAGE_ID = 'message';
const DOM_MESSAGE_CONTENT_ID = 'message_content';
const DOM_MESSAGE_TIME_ID = 'message_time';
const DOM_MESSAGE_USER_ID = 'message_user';

const DOM_BUTTON_MESSAGE_MORE = 'message_more';

const DOM_BUTTON_ROOM_ID = 'room_name_';

const DOM_ROOM_SELECTED = 'room_selected';
const DOM_ROOM_UNSELECTED = 'room_unselected';

const DOM_ROOM = (room_name, room_class) => {
    return `
        <li>
            <button onclick='room_change_button(this)'
            id='${DOM_BUTTON_ROOM_ID}${room_name}'>
            <p class='${room_class}'>${room_name}</p>
            </button>
        </li>`;
}

const DOM_MESSAGE = (message_content, message_data, user_name) => {
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

const DOM_MESSAGE_MORE = `
    <button id="${DOM_BUTTON_MESSAGE_MORE}" onclick='message_load()'>
        <h3>More</h3>
    </div>
`

//
const ROOM = document.getElementById(DOM_ROOM_ID);
const ROOM_ABLE = document.getElementById(DOM_ROOM_ABLE_ID);

const CHAT = document.getElementById(DOM_CHAT_ID);
const CHAT_FORMS = document.getElementById(DOM_CHAT_FORMS_ID);
const CHAT_INPUT = document.getElementById(DOM_CHAT_INPUT_ID);
const CHAT_MESSAGE = document.getElementById(DOM_CHAT_MESSAGE_ID);

const SERVER_STATUS = document.getElementById(DOM_SERVER_STATUS_ID);
const SERVER_STATUS_PULL = document.getElementById(DOM_SERVER_STATUS_PULL_ID);
