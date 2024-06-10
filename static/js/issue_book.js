function Return_book(T_id){
    console.log(T_id)
    const req=new XMLHttpRequest()
    req.open('Post','/issuebook')
    req.onload= ()=>{
        location.reload()
    }
    const data=new FormData()
    data.append("change_type","Book_Return")
    data.append("Transaction_id",T_id)
    req.send(data);
}
function Borrow_book(B_id,M_id){
    // console.log(B_id,M_id)
    const req=new XMLHttpRequest()
    req.open('Post','/issuebook')
    req.onload= ()=>{
        location.reload()
    }
    const data=new FormData()
    data.append("change_type","Book_Borrow")
    data.append("Book_id",B_id)
    data.append("Member_id",M_id)
    req.send(data);
}