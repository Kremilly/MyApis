function getFetchApis() {
    return fetch(`${window.location.origin}/json`).then(
        response => response.json()
    ).then( data => {
        $('#list').empty()
        
        $(el).addClass('actived')
        $('#cratesBtn').removeClass('actived')

        data.list.forEach( api => {
            $('#list').append(`
                <li class='li-name'>
                    <a href='${api.wiki}' class='api-name' target='_blank'>
                        ${api.name}
                        <div class='fas fa-arrow-up-right-from-square'></div>
                    </a>
                </li>
            `)
        })
    })
}

function getFetchCrates() {
    let userId = 232087

    return fetch(`https://crates.io/api/v1/crates?user_id=${ userId }`).then(
        response => response.json()
    ).then( data => {
        $('#list').empty()

        $(el).addClass('actived')
        $('#apisBtn').removeClass('actived')

        data.crates.forEach( crate => {
            $('#list').append(`
                <li class='li-name'>
                    <a href='https://crates.io/crates/${crate.name}' class='api-name' target='_blank'>
                        ${crate.name}
                        <div class='fas fa-arrow-up-right-from-square'></div>
                    </a>
                </li>
            `)
        })
    })
}