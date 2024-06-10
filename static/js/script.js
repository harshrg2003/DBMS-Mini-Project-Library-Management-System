function togglesublist(sublistId) {
    var sublist = document.getElementById(sublistId);
    if (sublist.style.display === 'none' || sublist.style.display === '') {
        sublist.style.display = 'block';
    } else {
        sublist.style.display = 'none';
    }
}

function Genre_popover(genres,element){
    // const container=document.getElementsByClassName("container")[0]
    // console.log(genres,element.getBoundingClientRect())
    rect=getElementAbsolutePos(element)
    const popover_elem=document.createElement("div")
    const width=200
    popover_elem.id="Genre_popover"
    popover_elem.style.position="absolute"
    popover_elem.style.top=rect.y+"px"
    popover_elem.style.left=(rect.x-width)+"px"
    popover_elem.style.minWidth=width+"px"
    popover_elem.style.maxWidth=width+"px"
    const list=document.createElement("ul")
    // list.className="genres"
    let maxw=0
    for(let i=0;i<genres.length;i++){
        let node=document.createElement("li")
        // node.className="genre_tag"
        node.innerText=genres[i]
        list.appendChild(node)
    }
    popover_elem.appendChild(list)
    // popover_elem.style.top=rect.y
    // popover_elem.style.left=rect.x
    // container.appendChild(popover_elem)
    document.body.appendChild(popover_elem)
}
function Genre_popover_remove(){
    const popover_elem=document.getElementById("Genre_popover")
    // console.log(popover_elem)
    popover_elem.remove()
}

function getElementAbsolutePos(element) {
    var res = new Object();
	res.x = 0; res.y = 0;
	if (element !== null) { 
        if (element.getBoundingClientRect) {
            var viewportElement = document.documentElement;  
            var box = element.getBoundingClientRect();
		    var scrollLeft = viewportElement.scrollLeft;
            var scrollTop = viewportElement.scrollTop;
            
		    res.x = box.left + scrollLeft;
		    res.y = box.top + scrollTop;
            
		}
	}
    return res;
}

function confirm_delete(id){
    data=prompt("Are you Sure you want to Delete?\nEnter 'DELETE' to confirm ")
    if (data=="DELETE"){
        const req=new XMLHttpRequest()
        req.open('Post','/books')
        req.onload= ()=>{
            location.reload()
        }
        const data=new FormData()
        data.append("change_type","Book_Delete")
        data.append("Book_id",id)
        req.send(data);
        return false
    }
    else{
        console.log("Failed to delete")
    }
}
function edit_book(id,genres,Book_genre,Book_authors,Book_title,edition,available){
    // console.log(Book_genre)
    if (genres==undefined){
        genres=[
            [1,"Fantasy"],
            [2,"Adventure"],
            [3,"Romance"],
            [4,"Contemporary"],
            [5,"Dystopian"],
            [6,"Mystery"],
            [7,"Horror"],
            [8,"Thriller"],
            [9,"Paranormal"],
            [10,"Historical fiction"],
            [11,"Science Fiction"],
            [12,"Children"],
            [13,"Memoir"],
            [14,"Cookbook"],
            [15,"Art"],
            [16,"Self-help"],
            [17,"Personal Development"],
            [18,"Motivational"],
            [19,"Health"],
            [20,"History"],
            [21,"Travel"],
            [22,"Guide"],
            [23,"Families and Relationships"],
            [24,"Humor"],
            [25,"Anthropology"],
            [26,"Astronomy"],
            [27,"Biography"],
            [28,"Business and Management"],
            [29,"Communication and Media Theory"],
            [30,"Crafts and Hobbies"],
            [31,"Cultural Studies"],
            [32,"Economics"],
            [33,"Education"],
            [34,"Essay"],
            [35,"Family and Parenting"],
            [36,"Film and Cinema Studies"],
            [37,"Gender Studies"],
            [38,"Gardening"],
            [39,"Journalism"],
            [40,"Linguistics"],
            [41,"Literary Criticism"],
            [42,"Mathematics"],
            [43,"Media Studies"],
            [44,"Music"],
            [45,"Nature Writing"],
            [46,"Philosophy"],
            [47,"Philosophy of Science"],
            [48,"Political Science"],
            [49,"Psychology"],
            [50,"Reference and Manuals"],
            [51,"Religion and Spirituality"],
            [52,"Science"],
            [53,"Science Communication"],
            [54,"Social Commentary"],
            [55,"Sociology"],
            [56,"Sports and Recreation"],
            [57,"Technology and Computers"],
            [58,"True Adventure"],
            [59,"True Crime"],
            [60,"Novel"],
            [61,"Short Story"],
            [62,"War"],
            [63,"Realism"],
            [64,"Fiction"],
            [65,"Quest"],
            [66,"Drama"]
            ]
    }
    const container=document.getElementsByClassName("container")[0]
    const bg_div=document.createElement("div")
    bg_div.id="outside_edit"
    const edit_div=document.createElement("div")
    edit_div.id="edit_window"
    bg_div.style.height=container.clientHeight+"px"
    bg_div.style.width=window.outerWidth+"px"
    // console.log(window.innerWidth)
    // console.log(container.clientHeight)
    bg_div.style.position="absolute"
    bg_div.style.backgroundColor="rgba(0,0,0,0.1)"
    bg_div.style.zIndex=3
    bg_div.style.top="0px"
    bg_div.style.left="0px"
    remove_edit_screen=()=>{bg_div.remove();edit_div.remove()}
    bg_div.onclick=remove_edit_screen
    // console.log(window.innerWidth)
    edit_div.onclick=()=>console.log(40)
    document.body.appendChild(bg_div)
    document.body.appendChild(edit_div)
    author_list=""
    for(let i=0;i<Book_authors.length-1;i++){
        author_list+=Book_authors[i]+',\n'
    }
    if (author_list !=undefined || author_list.length==0){
        author_list+=Book_authors[Book_authors.length-1]
    }
    edit_div.innerHTML='<div id="header_of_edit_window">Book Edit Menu</div>'+
    '<div id="edit_window_title">Title:<input id="edit_title" type="text" value="'+Book_title+'"></div>'+
    '<div id="edit_window_Author">Author:<textarea id="edit_author" type="text">'+author_list+'</textarea></div><br>'+
    '<div id="genrebox">Genre:<div id="select_genre_box"></div></div>'+
    '<div id="Submit_edits_button"><button onclick="send_edit_response('+id+')">Submit</button></div>'+
    '<div id="edit_edition_div">'+
        'Book Edition:<input id="edit_edition" type="number" value='+edition+' min=0>'+
    '</div>'+
    '<div id="edit_available_div">'+
        'Book is available:<input id="edit_available" type="checkbox" checked='+(available==1)+'>'+
    '</div>'
    
    const genre_box=document.getElementById("select_genre_box")
    for(let i=0;i<genres.length;i++){
        if ( Book_genre.indexOf(genres[i][1])!=-1){
            // console.log("found this genre "+genres[i][1])
            genre_box.innerHTML+="<input type=checkbox checked=true name="+genres[i][0]+">"+genres[i][1]+"<br>"
            // genre_box.innerHTML+="<input type=checkbox checked=true name='genre_select"+genres[i][0]+"'>"+genres[i][1]+"<br>"
        }
        else{
        genre_box.innerHTML+="<input type=checkbox name="+genres[i][0]+">"+genres[i][1]+"<br>"
        // genre_box.innerHTML+="<input type=checkbox name='genre_select"+genres[i][0]+"'>"+genres[i][1]+"<br>"
        }
    }
}


function send_edit_response(id){
    const req=new XMLHttpRequest()
    const data=new FormData()
    data.append("change_type","Book_Edit")
    data.append("Book_id",id)
    title=document.getElementById("edit_title").value
    data.append("Book_title",title)
    authors=document.getElementById("edit_author").value
    data.append("Book_authors",authors)
    available=document.getElementById("edit_available").checked
    data.append("Book_available",available)
    edition=document.getElementById("edit_edition").value
    data.append("Book_edition",edition)
    genres=[]
    temp=document.getElementById("select_genre_box").querySelectorAll('input')
    for(let i=0;i<temp.length;i++){
        if (temp[i].checked==true){
            genres.push(temp[i].name)
        }
    }
    data.append("Book_genres",genres)
    // console.log(data)
    // console.log(authors)
    temp_elem=0;
    // data.append()
    bg_div=document.getElementById("outside_edit");
    edit_div=document.getElementById("edit_window");
    bg_div.remove();
    edit_div.remove();
    req.open('Post','/books')
    req.onload= ()=>{
        location.reload()
    }
    req.send(data);
    return false
}