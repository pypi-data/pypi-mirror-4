import re

re_infobox_begin = re.compile(r'\s*\{\{[Ii]nfobox\s+film\s*')
re_infobox_end = re.compile(r'\s*\}\}\s*')
re_infobox_field = re.compile(r'\s*\|\s*([\w_]+)\s*=\s*(.+)')
def get_infobox_data(text):
    lines = text.splitlines()
    data = {}
    in_infobox = False
    for line in lines:
        if re_infobox_begin.match(line):
            in_infobox = True
            continue
        if in_infobox:
            match = re_infobox_field.match(line)
            if match:
                print(match.groups())
                #data[match.group(1)] = match.group(2)
                continue
            else:
                print('Cannot parse template param line')
                print(line)
            if re_infobox_end.match(line):
                return data
    return data


def run_test(text):
    print(get_infobox_data(text))

test = r"""
{{Infobox film
| name           = Team America: World Police
| image          = Team america poster 300px.jpg
| image_size     = 215px
| alt            = 
| caption        = Theatrical release poster
| director       = [[Trey Parker]]
| producer       = [[Trey Parker]]<br>[[Matt Stone]]<br>[[Scott Rudin]]
| writer         = Trey Parker<br />Matt Stone<br />Pam Brady
| starring       = Trey Parker<br />Matt Stone<br />[[Kristen Miller]]<br />[[Masasa Moyo|Masasa]]<br />[[Daran Norris]]<br />[[Phil Hendrie]]<br />[[Maurice LaMarche]]
| music          = [[Harry Gregson-Williams]]
| cinematography = [[Bill Pope]]
| editing        = Tom Vogt
| studio         = [[Scott Rudin|Scott Rudin Productions]]
| distributor    = [[Paramount Pictures]]
| released       = {{Film date|2004|10|14|[[Denver Film Festival|Denver]]|2004|10|15}}
| runtime        = 98 minutes
| country        = United States
| language       = English
| budget         = $32 million
| gross          = $50,907,422
}}
'''''Team America: World Police''''' is a 2004 [[Satire|satirical]] [[Action film#Action comedy|action comedy film]] written by [[Trey Parker]], [[Matt Stone]], and [[Pam Brady]] and directed by Parker, all of whom are also known for the popular animated television series ''[[South Park]]''. The film is a [[satire]] of big-budget [[action film]]s and their associated [[cliché]]s and [[stereotype]]s, with particular humorous emphasis on the global implications of [[Politics of the United States|US politics]]. The title of the film itself is derived from domestic and international political criticisms that the U.S. frequently and unilaterally tries to "[[American foreign policy|police the world]]". The film features a cast composed of [[marionette]]s. ''Team America'' focuses on a fictional team of political [[paramilitary]] policemen known as "Team America: World Police", who attempt to save the world from a violent terrorist plot led by [[Kim Jong-il]]. 

==External links==
{{wikiquote}}
* {{Official website|http://www.teamamerica.com}}
* {{IMDb title|0372588|Team America: World Police}}
* {{Bcdb|68495-Team_America_World_Police|Team America: World Police}}
* {{AllRovi movie|309182|Team America: World Police}}
* {{mojo title|teamamerica|Team America: World Police}}
* {{rotten-tomatoes|team_america_world_police|Team America: World Police}}
* [http://flakmag.com/film/teamamerica.html An analysis at Flakmagazine]
* [http://rogerebert.suntimes.com/apps/pbcs.dll/article?AID=/20041014/REVIEWS/40921007/1023 Roger Ebert's review]

{{Trey Parker and Matt Stone}}
{{Scott Rudin}}
{{Empire Award for Best Comedy}}
{{DEFAULTSORT:Team America - World Police}}
[[Category:2004 films]]
[[Category:2000s action films]]
[[Category:2000s adventure films]]
[[Category:2000s comedy films]]
[[Category:American films]]
"""

if __name__=='__main__':
    run_test(test)
