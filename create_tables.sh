mysql -u $1 -p$2 -h $3 -D $4 << EOF
#[SQL Commands]
use mysql;

CREATE TABLE t_conv (
	id int auto_increment primary key, 
	conv varchar(10) not null
);

CREATE TABLE t_prova (
	id int auto_increment primary key, 
	fase varchar(10) not null
);

CREATE TABLE t_assig_grau (
	id int auto_increment primary key,
	tipus varchar(10) not null
);


CREATE TABLE p_acces (
	nota float not null, #nota mitja de selectivitat
	any1 int not null, 
	any2 int not null, 
	id int auto_increment primary key,
	conv int not null,
	universitat varchar(50), 
	foreign key (conv) references t_conv(id)
);


CREATE TABLE assig_sel (
	codi int primary key, 
	nom varchar(70) not null
);

CREATE TABLE assig_prova (
	id_prova int,
	id_assig int, 
	nota float not null, 
	presentat boolean not null default false,
	fase int not null, 
	primary key (id_prova, id_assig),
	foreign key (id_prova) references p_acces(id), 
	foreign key (id_assig) references assig_sel(codi),
	foreign key (fase) references t_prova(id)	
);

CREATE TABLE alumne (
	id_alumne int auto_increment primary key, 
	mitja_exp float not null, 
	centre varchar(150),
	id_prova int,
	conv_batx int not null, 
	foreign key (id_prova) references p_acces(id),
	foreign key (conv_batx) references t_conv(id)
);


CREATE TABLE matricula (
	id int auto_increment primary key, 
	any1 int not null, 
	any2 int not null, 
	ordre_preferencia int not null,
	cred_1 int not null default 0, 
	cred_2 int not null default 0, 
	cred_3 int not null default 0, 
	cred_sup int not null default 0v, 
	cred_rec int not null default 0, 
	cred_pres int not null default 0, 
	cred_no_pres int not null default 0, 
	alumne int not null, 
	foreign key (alumne) references alumne(id)
);

CREATE TABLE grau (
	id_grau int primary key,
	nom varchar(70) not null, 
	pla varchar(30) not null
);

CREATE TABLE assig (
	id_assig int primary key
);

CREATE TABLE assig_grau (
	id_grau int, 
	id_assig int,
	curs int not null, 
	tipus int not null, 
	credits int not null,
	primary key (id_grau, id_assig),
	foreign key (tipus) references t_assig_grau(id),
	foreign key (id_grau) references grau(id_grau),
	foreign key (id_assig) references assig(id_assig)  
);

CREATE TABLE alumne_assig (
	id_alumne int, 
	id_assig int, 
	any1 int not null, 
	any2 int not null, 
	conv int, 
	nota float not null default 0,
	m_honor boolean default false, 
	presentat boolean not null default false, 
	primary key (id_alumne, id_assig) ,
	foreign key (id_alume) references alumne(id_alumne), 
	foreign key (id_assig) references assig(id_assig), 
	foreign key (conv) references t_conv(id) 
);


EOF
