"""
中英文对照字典（极速、零依赖）
如需翻译更多书籍/作者，直接在下面字典里添加即可
"""
import pandas as pd

# ---- 书名映射 ----
TITLE_MAP = {
    "The Sword in the Stone": "石中剑",
    "Memories of Ice": "冰之记忆",
    "Green Gem": "绿宝石",
    "Radiance": "光芒",
    "Chloe's Purpose": "克洛伊的使命",
    "All the Young Dudes": "所有年轻人",
    "The Alchemy Fire Murder": "炼金术之火谋杀案",
    "100 Fun Bible Facts": "100个有趣的圣经事实",
    "Mark of the Lion Trilogy": "狮子的印记三部曲",
    "Klaeber's Beowulf": "克莱伯的贝奥武夫",
    "The Devil's Deceptions": "魔鬼的欺骗",
    "Illuminated: Figurative Art by Jia Lu": "照亮：贾璐的具象艺术",
    "CEO-Stories": "CEO故事",
    "Jubal's Field Trip To Heaven": "朱巴尔的天堂实地考察之旅",
    "Lamb: The Gospel According to Biff": "羔羊：比夫福音",
    "Harry Potter and the Sorcerer's Stone": "哈利·波特与魔法石",
    "The Hunger Games": "饥饿游戏",
    "Twilight": "暮光之城",
    "The Hobbit": "霍比特人",
    "1984": "1984",
    "Animal Farm": "动物农场",
    "Pride and Prejudice": "傲慢与偏见",
    "The Great Gatsby": "了不起的盖茨比",
    "To Kill a Mockingbird": "杀死一只知更鸟",
    "The Catcher in the Rye": "麦田里的守望者",
}

# ---- 作者映射 ----
AUTHOR_MAP = {
    "Walt Disney Company": "华特迪士尼公司",
    "Christopher Moore": "克里斯托弗·摩尔",
    "Steven Erikson": "史蒂文·埃里克森",
    "Grace Draven": "格蕾丝·德拉文",
    "Susan Rowland": "苏珊·罗兰",
    "Julie Mannino": "朱莉·曼尼诺",
    "George Orwell": "乔治·奥威尔",
    "J.K. Rowling": "J.K.罗琳",
    "Stephen King": "斯蒂芬·金",
    "Agatha Christie": "阿加莎·克里斯蒂",
    "J.R.R. Tolkien": "J.R.R.托尔金",
    "Jane Austen": "简·奥斯汀",
    "F. Scott Fitzgerald": "菲茨杰拉德",
    "Harper Lee": "哈珀·李",
    "Suzanne Collins": "苏珊·柯林斯",
    "Stephenie Meyer": "斯蒂芬妮·梅尔",
    "Sarah J. Maas": "莎拉·J·马斯",
    "Colleen Hoover": "科琳·胡佛",
    "Leigh Bardugo": "利·巴杜戈",
    "Cassandra Clare": "卡桑德拉·克莱尔",
    "Haruki Murakami": "村上春树",
    "Kristin Hannah": "克里斯汀·汉娜",
    "Anonymous": "佚名",
}

def translate_title(en_title):
    if not isinstance(en_title, str):
        return en_title
    return TITLE_MAP.get(en_title.strip(), en_title)

def translate_author(en_author):
    if not isinstance(en_author, str):
        return en_author
    return AUTHOR_MAP.get(en_author.strip(), en_author)