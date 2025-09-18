import * as index from './index_globals.js';

index.SERVER_STATUS.addEventListener('click', (e) => {
    e.preventDefault();

    //
    if(index.SERVER_STATUS.className == 'server_status_expand'){
        index.SERVER_STATUS.className = 'server_status_neutral';
        index.CHAT.className = 'chat_neutral';
    } else{
        index.SERVER_STATUS.className = 'server_status_expand';
        index.CHAT.className = 'chat_reduce';
    }
});
