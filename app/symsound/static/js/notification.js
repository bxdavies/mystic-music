function notification(category, message) 
{
    
    if (category == 'success')
    {
        SimpleNotification.success({
            text: message
        })
    }
    else if (category == 'error')
    {
        SimpleNotification.error({
            text: message
        })
    }
    else if (category == 'info')
    {
        SimpleNotification.info({
            text: message
        })
    }
    else if (category == 'warning')
    {
        SimpleNotification.warning({
            text: message
        })
    }
    else if (category == 'message')
    {
        SimpleNotification.message({
            text: message
        })
    }
    else
    {
        console.error('Unknown category')
    }
}