create database teamtest; !!���ۂ�DB���Ƃ͈قȂ�܂�!!
!!����sql�ł̓f�[�^��ǉ�����ۂɑS�Ă̒l����͂���value���Ă��܂����A
auto_increment���g�p����Ă���J�����ɂ͒l��ݒ肹���Ƀf�[�^��ǉ����Ă�������!!



�����e�[�u��
create table department(
	department_id integer(2),
	department_name varchar(10) not null,
	primary key(department_id)
);

�E�����e�[�u��insert��
insert into department values (1,'�c�ƕ�');

��E�e�[�u��
create table official_position(
	position_id integer(2) primary key,
	position_name varchar(10) not null
);

�E��E�e�[�u��insert��
insert into official_position values(1,'�В�');
insert into official_position values(2,'�햱�����');
insert into official_position values(3,'����');
insert into official_position values(4,'��C');
insert into official_position values(5,'��ʎЈ�');


���p�҃e�[�u��
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

�A�J�E���g�o�^���
<insert into user(mail,name,department_id,superior_mail,position_id) values(���͒l�������Ă���j;>

�A�J�E���g�Ǘ����
<select * from user;> !!�\��������͎����A��E�A���[���A�h���X�A��i�̃��[���A�h���X�݂̂����A�������邽�߂̒l�Ƃ��āA�e�[�u�����̑S�Ă̏��������Ă���!!
<select position_name from official_position where position_id=(��̃Z���N�g�����玝���Ă���position_id);>

�A�J�E���g���ύX���
<update user set mail=(),name=(),position_id=(),superior_mail=(),department_id=() where user_id=(���X�g���玝���Ă���user_id);>

�A�J�E���g�폜
<delete from user where user_id=(���X�g���玝���Ă���user_id);>

!!�A�J�E���g���폜����ۂ��g�c���e�[�u���⏳�F�e�[�u���ŊO���L�[�Ƃ��ēo�^���Ă���usre_id���������Ƃ��ł��Ȃ��悤�Ȃ̂ŁA
���[�U���폜����ꍇ�ɂ͂�ނ𓾂��A�g�c���e�[�u���Ȃǂ�user_id�Ƃ��Ďg�p����Ă���f�[�^���폜����K�v������!!

<delete from approval_document where user_id=(���X�g���玝���Ă���user_id);> 
<delete from approval where user_id=(���X�g���玝���Ă���user_id);> 

�p�X���[�h�ύX�i�\���g���ꂽ�p�X���[�h��saltpass); !!�p�X���[�h�ύX�̍ۂɓ��͂����p�X���[�h���n�b�V���������̂ƈ�v���郆�[�U��T��!!
<update user set password=(���͒l��saltpass) where (���[���A�h���X�Ȃǂ̌l�����ł�����̂ŏ����w��);>

�E���p�҃e�[�u��insert��
<insert into user values(1,"y.suzuki.sys20@morijyobi.ac.jp","��ؘА^","797a9y8ayds9ha8hh8",1,1,"s.yamamoto.sys20@morijyobi.ac.jp","salt",1);>

�g�c���e�[�u��
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
	result integer(2), //�\���O��null,���F�҂�=0,���F��1,�ی�=2//
	authorizer_id integer(6) not null,
	foreign key (authorizer_id)
	references user(user_id),
	preferred_day date not null
	);
	
	
�E�g�c���e�[�u��insert��
insert into approval_document(user_id,document_name,application_date,contents,quaritity,price,total_payment,
reason,comment,result,authorizer_id,preferred_day) 
value(1,"�g�c��",sysdate(),"�g�c���e�ł�",100,400000,40000000,"���R�ł�","�R�����g�ł�",0,5,(�C�ӂ̓��t));


�g�c���Ǘ��V�X�e���E�Z���N�g��
<select document_id, document_name, application_date, user_id, comment, result,authorizer_id, preferred_day from approval_document; >
<select name from user where user_id=user_id(��̃Z���N�g���Ŏ����Ă������́j;>
<select name from user where user_id=authorizer_id(�S���Җ��j;>

�������g�c���������\������ԂŌ���
<select document_id, document_name, application_date, user_id, comment, result,authorizer_id, preferred_day from approval_document where result=(�����l);>

�S�̂��g�c��������or���g�p���ă��[�h����
<select document_id, document_name, application_date, user.name, comment, result,authorizer_id, preferred_day from approval_document where user_id=(�����l) or application_date=(�����l);> !!�����l�Ƃ��Ďg�p���������̂�where�ɐݒ肵�Ă�������!!
!!user_id��result�Adocument_id�ȂǂŌ������悤�Ƃ����ہA1��2�Ȃǌ����l������Ă��܂��̂ŁA������or�œ����ɐݒ肷�邱�Ƃ͂ł��Ȃ�!!
!!�\�ߌ������邽�߂̒l�����߂Ēu���A(��������Ȃǂ�)where���ɐݒ肵�Ă���Ζ��Ȃ�!!

�g�c�����e�̃R�����g�ۑ��A�ύX
//�g�c���Ǘ��V�X�e���E�Z���N�g���œ��肵�Ă���document_id���g��//
<update approval_document set comment=(���͒l) where document_id=();>

���F�e�[�u��
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
	
�E���F�e�[�u��insert��
insert into approval values(1,1,"2020-06-24",1,1);
�����̓��t���擾����֐�=sysdate()