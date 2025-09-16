SERVER_STATUS.addEventListener('click', (e) => {
    e.preventDefault();

    //
    if(SERVER_STATUS.className == 'server_status_expand'){
        SERVER_STATUS.className = 'server_status_neutral';
        CHAT.className = 'chat_neutral';
    } else{
        SERVER_STATUS.className = 'server_status_expand';
        CHAT.className = 'chat_reduce';
    }
});
