drop database if exists Library;
create database Library;
use Library;
create table Book(
	Book_id int auto_increment,
    Title varchar(200) not null,
    Edition int,
    Available bool default true,
    constraint pk1 primary key(Book_id)
);
create table Author(
	Author_id int auto_increment,
    Author_name varchar(200),
    constraint pk2 primary key(Author_id)
);
create table Publisher(
	Publisher_id int auto_increment,
    Publisher_name varchar(200),
    Publisher_phone varchar(20),
    Publisher_address varchar(200),
    constraint pk3 primary key(Publisher_id)
);
create table Library_member(
	Member_id int auto_increment,
    Fname varchar(30) not null,
    Mname varchar(30),
    Lname varchar(30),
    Membership_level int default 1,
    Books_taken int default 0,
    constraint pk4 primary key(Member_id)
);
create table Borrowed_by(
	Transaction_id int auto_increment,
    Due_date date,
    Borrowing_date date,
    Book_id int,
    Member_id int,
    returned bool default False,
	constraint pk5 primary key(Transaction_id),
    constraint fk1 foreign key(Book_id) references Book(Book_id),
    constraint fk2 foreign key(Member_id) references Library_member(Member_id)
);
create table Written_by(
	Author_id int,
    Book_id int,
	constraint pk6 primary key(Book_id,Author_id),
    constraint fk3 foreign key(Book_id) references Book(Book_id) on delete cascade,
    constraint fk4 foreign key(Author_id) references Author(Author_id)
);
alter table Book add column Publisher_id int;
alter table Book add constraint fk5 foreign key(Publisher_id) references Publisher(Publisher_id);

create table Genre(
	Genre_id int,
    Genre_name varchar(30),
    constraint pk7 primary key(Genre_id)
);

create table Book_genre(
	Book_id int,
    Genre_id int,
    constraint pk8 primary key(Book_id,Genre_id),
    constraint fk6 foreign key(Book_id) references Book(Book_id) on delete cascade,
    constraint fk7 foreign key(Genre_id) references Genre(Genre_id)
);
create table Member_address(
	Member_id int,
    address varchar(200) not null,
    constraint pk9 primary key(Member_id,address),
    constraint fk8 foreign key(Member_id) references Library_member(Member_id) on delete cascade
);
create table Member_email(
	Member_id int,
    email varchar(70) not null,
    constraint pk10 primary key(Member_id,email),
    constraint fk9 foreign key(Member_id) references Library_member(Member_id) on delete cascade
);
create table Member_phone_number(
	Member_id int,
    phone varchar(15) not null,
    constraint pk11 primary key(Member_id,phone),
    constraint fk10 foreign key(Member_id) references Library_member(Member_id) on delete cascade
);
create table user_cred(
	id int,
    user_name varchar(30) unique not null,
    last_login date default "2000-01-01",
    password varchar(30) not null,
    constraint pk12 primary key(id),
    constraint fk11 foreign key(id) references Library_member(Member_id) on delete cascade
);
create table test(
    id int auto_increment,
    name varchar(30),
    password varchar(1000),
    primary key(id)
);

#create view users as select user_name,last_login from user_cred;
delimiter // 
create function Can_Borrow(Member_id INT) RETURNS boolean deterministic
begin   
    declare member_level boolean;
    declare borrowed int;
    select M.Membership_level into member_level FROM library_member M WHERE M.Member_id = Member_id; 
	select M.Books_taken into borrowed FROM library_member M WHERE M.Member_id = Member_id;  
    if(member_level <=> 1) then 
        if(borrowed < 3) then 
            return true;
        else
            return false;
        end if;
    elseif(member_level <=> 2) then 
        if(borrowed < 7) then 
            return true;
        else
            return false;
        end if;
    elseif(member_level <=> 3) then 
        if(borrowed < 20) then 
            return true;
        else
            return false;
        end if;
    end if;
    return false;
end// 

create trigger returned
after update on library.borrowed_by
for each row
begin
	if(new.returned<=>True) then 
		update library.book B set B.Available = true where B.Book_id=new.Book_id;
        update library.library_member M set M.Books_taken=M.Books_taken-1 where M.Member_id=new.Member_id;
    end if;
end;//

create trigger borrowed
before insert on library.borrowed_by
for each row
begin
	declare member_level int; 
    if exists(select * from library_member where Member_id=new.Member_id) then
        if exists(select * from book where Book_id=new.Book_id and Available=True) then
            if Can_Borrow(new.Member_id) then
                set new.Borrowing_date=curdate();
                update book set Available=false where Book_id=new.Book_id;
                update library_member set Books_taken=Books_taken+1 where Member_id=new.Member_id ;
                select M.Membership_level into member_level FROM library_member M WHERE M.Member_id = new.Member_id; 
                if (member_level<=>1) then
					set new.Due_date=DATE_ADD(new.Borrowing_date,interval 7 day);
                elseif (member_level<=>2) then
					set new.Due_date=DATE_ADD(new.Borrowing_date,interval 21 day);
                elseif (member_level<=>3) then
					set new.Due_date=DATE_ADD(new.Borrowing_date,interval 60 day);
                end if;
            else
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'You can not Borrow more books';
            end if;
        else
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Book Not Available';
        end if;   
    end if;   
end//


create procedure library.signup(in user_name varchar(30),in password varchar(30),in fname varchar(30),in mname varchar(30),in lname varchar(30),in email varchar(70),in phone varchar(15),in address varchar(200)) 
begin
	if not exists( select * from library.user_cred L where L.user_name=user_name)then
		insert into library.library_member(fname,mname,lname) values(fname,mname,lname);
		set @id=last_insert_id();
		insert into library.user_cred(id,user_name,password,last_login) values(@id,user_name,password,curdate());
		insert into library.member_address(Member_id,address) values(@id,address);
		insert into library.member_email(Member_id,email) values(@id,email);
		insert into library.member_phone_number(Member_id,phone) values(@id,phone);
    else
		select "User Already Exists" data;
    end if;
end//


create procedure library.login(in user_name varchar(30),in password varchar(30)) 
begin
	if exists( select * from library.user_cred L where L.user_name=user_name)then
		if exists(select * from library.user_cred L where L.user_name=user_name and Binary L.password=password) then
			select L.id as uid from library.user_cred L where L.user_name=user_name and L.password=password;
		else
			select "Wrong Password" data;
		end if;
    else
		select "User Doesn't Exists" data;
    end if;
end//
delimiter ;



insert into library.library_member(Member_id,Fname,Mname,Lname,membership_level) values(1001,'James','','Ackerson',2);
insert into library.member_address values(1001,'Bightin House, 4th Avenue');
insert into library.member_email values(1001,'james@gmail.com');
insert into library.member_phone_number values(1001,'+448836937399');

insert into library.member_address values(1001,'Draing House, 7th street');
insert into library.member_email values(1001,'james@yahoo.com');
insert into library.member_phone_number values(1001,'+448446936799');

insert into library.member_address values(1001,'#403, Lutan Apartments, Luten');
insert into library.member_email values(1001,'destroyer@gmail.com');
insert into library.member_phone_number values(1001,'+443839397698');

insert into library.library_member(fname,mname,lname,membership_level) values('James','Stone','Hyoren',3);
insert into library.user_cred(id,user_name,password) values (last_insert_id(),"jamesj","Lib_pass1");

insert into library.library_member(fname,mname,lname) values('Alan','George','Jimcy');
insert into library.user_cred(id,user_name,password) values (last_insert_id(),"Alan","Welcome1");

insert into library.library_member(fname,mname,lname) values('Kevin','','Mathew');
insert into library.user_cred(id,user_name,password) values (last_insert_id(),"Kal","kalo2006M");

# this is an example of how to call the signnup procedure, if it returns nothing, signup is successful
#		if signup is not successful, it returns a record of value "User Already Exists"
call library.signup("user_name","password","fname","mname","lname","email","phone number","address");
# use library.login("user_name","password"); to get the id of that user under column name uid
#		if user doesn't exists or password is wrong, the returned table has a column called data
#				 that tells the problem with input values


insert into library.Publisher values
(1,"Fingerprint! Publishing","+9111-23265358","Prakash Books India Pvt Ltd, 113A, Ansari Road, Daryaganj, New Delhi-110002"),
(2,"Cambridge University Press","+44(0)1223 553311","Cambrudge University Press & Asssessment, Shaftesbury Road, Cambridge, CB28EA"),
(3,"Charles Scribner's Sons",Null,"153-157 Fifth Avenue, New York City, U.S."),
(4,"New Age International Publishers",Null,"New Age International Pvt Ltd, Malliarjuna Tmeple Street,NR Colony, Basavangudi, Bengaluru, Karnataka, India"),
(5,"HarperTorch","+55 21 3175-1030","R. da Quitanda, 86 - Centro, Rio de Janeiro - RJ, 20091-005"),
(6,"Prentice - Hall","+60 3-567333159","11A, Jalan PJS 7/19Taman Bandar Sunway, 46150 Petaling Jaya, Selangor, Malaysia");

Insert into library.author(Author_id,Author_name) values 
(1,"Earnest Hemingway"),
(2,"Leo Tolstoy"),
(3,"Paulo Cohelo"),
(4,"M. Govindarajan"),
(5,"S. Natarajan"),
(6,"B. Ram"),
(7,"Sanjay Kumar"),
(8,"Steven L Brunton"),
(9,"J. Nathan Kutz");
insert into library.Book(Book_id,Title,Edition,Publisher_id) values
(1,"War and Peace",4,1),
(2,"War and Peace",1,1),
(3,"Anna Karenina",3,1),
(4,"For Whom The Bell Tolls",4,3),
(5,"The Alchemist",19,5),
(6,"Engineering Ethics",6,6),
(7,"Computer Fundamentals:Architecture and Organisation",6,4),
(8,"Data-Driven Science and Engineering: Machine Learning, Dynamic Systems and Control",2,2)
;
insert into library.written_by(Book_id,Author_id) values
(1,2),
(2,2),
(3,2),
(4,1),
(5,3),
(6,4),
(6,5),
(7,6),
(7,7),
(8,9)
;

insert into library.genre values
(1,"Fantasy"),
(2,"Adventure"),
(3,"Romance"),
(4,"Contemporary"),
(5,"Dystopian"),
(6,"Mystery"),
(7,"Horror"),
(8,"Thriller"),
(9,"Paranormal"),
(10,"Historical fiction"),
(11,"Science Fiction"),
(12,"Children"),
(13,"Memoir"),
(14,"Cookbook"),
(15,"Art"),
(16,"Self-help"),
(17,"Personal Development"),
(18,"Motivational"),
(19,"Health"),
(20,"History"),
(21,"Travel"),
(22,"Guide"),
(23,"Families and Relationships"),
(24,"Humor"),
(25,"Anthropology"),
(26,"Astronomy"),
(27,"Biography"),
(28,"Business and Management"),
(29,"Communication and Media Theory"),
(30,"Crafts and Hobbies"),
(31,"Cultural Studies"),
(32,"Economics"),
(33,"Education"),
(34,"Essay"),
(35,"Family and Parenting"),
(36,"Film and Cinema Studies"),
(37,"Gender Studies"),
(38,"Gardening"),
(39,"Journalism"),
(40,"Linguistics"),
(41,"Literary Criticism"),
(42,"Mathematics"),
(43,"Media Studies"),
(44,"Music"),
(45,"Nature Writing"),
(46,"Philosophy"),
(47,"Philosophy of Science"),
(48,"Political Science"),
(49,"Psychology"),
(50,"Reference and Manuals"),
(51,"Religion and Spirituality"),
(52,"Science"),
(53,"Science Communication"),
(54,"Social Commentary"),
(55,"Sociology"),
(56,"Sports and Recreation"),
(57,"Technology and Computers"),
(58,"True Adventure"),
(59,"True Crime"),
(60,"Novel"),
(61,"Short Story"),
(62,"War"),
(63,"Realism"),
(64,"Fiction"),
(65,"Quest"),
(66,"Drama");

insert into book_genre values
(1,60),
(1,10),
(1,3),
(1,62),
(1,46),
(1,20),
(2,60),
(2,10),
(2,3),
(2,62),
(2,46),
(2,20),
(3,60),
(3,63),
(3,64),
(4,60),
(4,62),
(4,64),
(5,60),
(5,65),
(5,66),
(5,1),
(5,64),
(5,2),
(6,57),
(7,57),
(7,52),
(8,57),
(8,52)
;
