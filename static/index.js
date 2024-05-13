$( e => {

    $('#search-input').on('input', function () {
        var searchText = $(this).val().toLowerCase()

        $('#list li').each( function () {
            var listItemText = $(this).text().toLowerCase()

            if (listItemText.includes(searchText)) {
                $(this).show()
            } else {
                $(this).hide()
            }
        })
    })

    $('#search-bar-toggle').click( function () {
        $(this).toggleClass('showed')
        
        $('#menu-box-toggle').removeClass('showed')
        
        $('#menu-box').slideUp(250)
        $('#search-bar').slideToggle(250)
        
        $('input').focus()
    })

    $('#menu-box-toggle').click( function () {
        $(this).toggleClass('showed')
        $('#search-bar-toggle').removeClass('showed')

        $('#search-bar').slideUp(250)
        $('#menu-box').slideToggle(250)
    })

})