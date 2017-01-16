# coding: utf-8

CREATE_CMD = ('create table if not exists co2meter '
              '(time datetime, ppm integer, response varchar(255))')

ADD_ROW_CMD = ('insert into co2meter (time, ppm, response) '
               'values("{0}", {1}, "{2}")')
