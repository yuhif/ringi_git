create database teamtest; !!実際のDB名とは異なります!!
!!このsqlではデータを追加する際に全ての値を入力してvalueしていますが、
auto_incrementが使用されているカラムには値を設定せずにデータを追加してください!!



部署テーブル
create table department(
	department_id integer(2),
	department_name varchar(10) not null,
	primary key(department_id)
);

・部署テーブルinsert文
insert into department values (1,'営業部');

役職テーブル
create table official_position(
	position_id integer(2) primary key,
	position_name varchar(10) not null
);

・役職テーブルinsert文
insert into official_position values(1,'社長');
insert into official_position values(2,'常務取締役');
insert into official_position values(3,'部長');
insert into official_position values(4,'主任');
insert into official_position values(5,'一般社員');


利用者テーブル
create table user(
	user_id integer(6) primary key auto_increment,
	mail varchar(254) not null unique,
	name varchar(32) not null,
	password varchar(64) not null,
	department_id integer,
	foreign key (department_id) 
	references department(department_id),
	position_id integer,
	foreign key (position_id) 
	references official_position(position_id),
	superior_mail varchar(64),
	salt varchar(64) not null,
	auth integer(2) not null
);

アカウント登録画面
<insert into user(mail,name,department_id,superior_mail,position_id) values(入力値を持ってくる）;>

アカウント管理画面
<select * from user;> !!表示する情報は氏名、役職、メールアドレス、上司のメールアドレスのみだが、検索するための値として、テーブル内の全ての情報を持ってくる!!
<select position_name from official_position where position_id=(上のセレクト文から持ってきたposition_id);>

アカウント情報変更画面
<update user set mail=(),name=(),position_id=(),superior_mail=(),department_id=() where user_id=(リストから持ってきたuser_id);>

アカウント削除
<delete from user where user_id=(リストから持ってきたuser_id);>

!!アカウントを削除する際に稟議書テーブルや承認テーブルで外部キーとして登録してあるusre_idを消すことができないようなので、
ユーザを削除する場合にはやむを得ず、稟議書テーブルなどでuser_idとして使用されているデータも削除する必要がある!!

<delete from approval_document where user_id=(リストから持ってきたuser_id);> 
<delete from approval where user_id=(リストから持ってきたuser_id);> 

パスワード変更（ソルトされたパスワード＝saltpass); !!パスワード変更の際に入力したパスワードをハッシュしたものと一致するユーザを探す!!
<update user set password=(入力値のsaltpass) where (メールアドレスなどの個人を特定できるもので条件指定);>

・利用者テーブルinsert文
<insert into user values(1,"y.suzuki.sys20@morijyobi.ac.jp","鈴木侑真","797a9y8ayds9ha8hh8",1,1,"s.yamamoto.sys20@morijyobi.ac.jp","salt",1);>

稟議書テーブル
create table approval_document(
	document_id integer(10) primary key auto_increment,
	user_id integer,
	foreign key (user_id)
	references user(user_id),
	document_name varchar(32) not null,
	application_date date not null,
	contents varchar(256) not null,
	quaritity integer(6) not null,
	price integer(8) not null,
	total_payment integer(10) not null,
	reason varchar(256) not null,
	comment varchar(256),
	result integer(2), //申請前＝null,承認待ち=0,承認＝1,否決=2//
	authorizer_id integer(6) not null,
	foreign key (authorizer_id)
	references user(user_id),
	preferred_day date not null
	);
	
	
・稟議書テーブルinsert文
insert into approval_document(user_id,document_name,application_date,contents,quaritity,price,total_payment,
reason,comment,result,authorizer_id,preferred_day) 
value(1,"稟議書",sysdate(),"稟議内容です",100,400000,40000000,"理由です","コメントです",0,5,(任意の日付));


稟議書管理システム・セレクト文
<select document_id, document_name, application_date, user_id, comment, result,authorizer_id, preferred_day from approval_document; >
<select name from user where user_id=user_id(上のセレクト文で持ってきたもの）;>
<select name from user where user_id=authorizer_id(担当者名）;>

自分の稟議書検索→申請書状態で検索
<select document_id, document_name, application_date, user_id, comment, result,authorizer_id, preferred_day from approval_document where result=(検索値);>

全体の稟議書検索＝orを使用してワード検索
<select document_id, document_name, application_date, user.name, comment, result,authorizer_id, preferred_day from approval_document where user_id=(検索値) or application_date=(検索値);> !!検索値として使用したいものをwhereに設定してください!!
!!user_idやresult、document_idなどで検索しようとした際、1や2など検索値が被ってしまうので、これらをorで同時に設定することはできない!!
!!予め検索するための値を決めて置き、(条件分岐などで)where分に設定していれば問題ない!!

稟議書内容のコメント保存、変更
//稟議書管理システム・セレクト文で入手しているdocument_idを使う//
<update approval_document set comment=(入力値) where document_id=();>

承認テーブル
create table approval(
	approval_id integer(10) primary key auto_increment,
	user_id integer,
	foreign key (user_id)
	references user(user_id),
	approval_day date,
	result integer(2),
	document_id integer,
	foreign key (document_id)
	references Approval_document(document_id)
	);
	
・承認テーブルinsert文
insert into approval values(1,1,"2020-06-24",1,1);
今日の日付を取得する関数=sysdate()