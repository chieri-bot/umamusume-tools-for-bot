import umamusume_bot
import umamusume_skill_parser as usp


"""
pr = usp.UmaSkillCodeParser("cn")
# print(pr.get_nature_lang("is_finalcorner==1 &corner!=0 &order_rate>=50 &order_rate<=80 &change_order_onetime<0"))
print(pr.get_nature_lang("distance_rate>=50 &order_rate>=40 &order_rate<=80"))
exit()


db = umamusume_bot.load_db("./pretty-derby/src/assert/db.json")
skills = db.skills
for s in skills:

    r = pr.get_nature_lang(s.condition)
    print(s.name, 1, r)
    if s.condition2 is not None and s.condition2 != "":
        r = pr.get_nature_lang(s.condition2)
        print(s.name, 2, r)

exit()
"""
# db = umamusume_bot.load_db("./pretty-derby/src/assert/db.json")
# print(umamusume_bot.update_database())

# umamusume_bot.image_generate.Generator.generate_event_table(name="チーム総合力アップ・最高の差し入れ").save("evt.png")
# exit()

gacha = umamusume_bot.image_generate.Gacha()
print(gacha.generate_image_card_well())
exit()

ug = umamusume_bot.image_generate.Generator("寄寄子")
ug.get_uma_info()
exit()
# ug.draw_skill_icon(20013, "憧れは桜を越える！", 2).save("tt.png")
db = umamusume_bot.load_db("./pretty-derby/src/assert/db.json")

skill = umamusume_bot.image_generate.SkillDrawer("翘尾巴")
# skill = umamusume_bot.image_generate.SkillDrawer(skill_data=db.skills[317])
skill.generate_skill_image(True).save("sktable.png")

pass
