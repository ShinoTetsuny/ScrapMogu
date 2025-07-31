import generateResponse from "../src/api/scrap/utils/generateResponse.js";
import { describe, expect, jest } from "@jest/globals";

const text = `<div class="main-page-categories">
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Bosses" title="Category:Bosses"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/b/b9/ZW_Main_Page_Bosses_Icon.png/revision/latest?cb=20210807235048&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element" data-image-name="ZW Main Page Bosses Icon.png" data-image-key="ZW_Main_Page_Bosses_Icon.png" data-relevant="0"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Bosses" title="Category:Bosses">Bosses</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Characters" title="Category:Characters"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/e/e6/ZW_Main_Page_Characters_Icon.png/revision/latest?cb=20210807235115&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Characters Icon.png" data-image-key="ZW_Main_Page_Characters_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/e/e6/ZW_Main_Page_Characters_Icon.png/revision/latest?cb=20210807235115"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Characters" title="Category:Characters">Characters</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Dungeons" title="Category:Dungeons"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/b/ba/ZW_Main_Page_Dungeons_Icon.png/revision/latest?cb=20210807235152&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Dungeons Icon.png" data-image-key="ZW_Main_Page_Dungeons_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/b/ba/ZW_Main_Page_Dungeons_Icon.png/revision/latest?cb=20210807235152"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Dungeons" title="Category:Dungeons">Dungeons</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Enemies" title="Category:Enemies"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/2/28/ZW_Main_Page_Enemies_Icon.png/revision/latest?cb=20210807235217&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Enemies Icon.png" data-image-key="ZW_Main_Page_Enemies_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/2/28/ZW_Main_Page_Enemies_Icon.png/revision/latest?cb=20210807235217"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Enemies" title="Category:Enemies">Enemies</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Items" title="Category:Items"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/c/c9/ZW_Main_Page_Items_Icon.png/revision/latest?cb=20210807235328&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Items Icon.png" data-image-key="ZW_Main_Page_Items_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/c/c9/ZW_Main_Page_Items_Icon.png/revision/latest?cb=20210807235328"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Items" title="Category:Items">Items</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Locations" title="Category:Locations"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/1/1e/ZW_Main_Page_Locations_Icon.png/revision/latest?cb=20210808001126&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Locations Icon.png" data-image-key="ZW_Main_Page_Locations_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/1/1e/ZW_Main_Page_Locations_Icon.png/revision/latest?cb=20210808001126"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Locations" title="Category:Locations">Locations</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Merchandise" title="Category:Merchandise"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/f/fd/ZW_Main_Page_Merchandise_Icon.png/revision/latest?cb=20210807235541&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Merchandise Icon.png" data-image-key="ZW_Main_Page_Merchandise_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/f/fd/ZW_Main_Page_Merchandise_Icon.png/revision/latest?cb=20210807235541"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Merchandise" title="Category:Merchandise">Merchandise</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Mini-Games" title="Category:Mini-Games"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/7/75/ZW_Main_Page_Mini-Games_Icon.png/revision/latest?cb=20210807235652&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Mini-Games Icon.png" data-image-key="ZW_Main_Page_Mini-Games_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/7/75/ZW_Main_Page_Mini-Games_Icon.png/revision/latest?cb=20210807235652"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Mini-Games" title="Category:Mini-Games">Mini-Games</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Plot_Events" title="Category:Plot Events"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/9/99/ZW_Main_Page_Events_Icon.png/revision/latest?cb=20210807235244&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Events Icon.png" data-image-key="ZW_Main_Page_Events_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/9/99/ZW_Main_Page_Events_Icon.png/revision/latest?cb=20210807235244"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Plot_Events" title="Category:Plot Events">Plot Events</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Races" title="Category:Races"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/0/03/ZW_Main_Page_Races_Icon.png/revision/latest?cb=20210807235805&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Races Icon.png" data-image-key="ZW_Main_Page_Races_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/0/03/ZW_Main_Page_Races_Icon.png/revision/latest?cb=20210807235805"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Races" title="Category:Races">Races</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Side_Quests" title="Category:Side Quests"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/7/78/ZW_Main_Page_Side_Quests_Icon.png/revision/latest?cb=20210807235834&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Side Quests Icon.png" data-image-key="ZW_Main_Page_Side_Quests_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/7/78/ZW_Main_Page_Side_Quests_Icon.png/revision/latest?cb=20210807235834"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Side_Quests" title="Category:Side Quests">Side Quests</a></div>
</div>
<div class="main-page-category-item">
<div class="main-page-category-item-image"><span typeof="mw:File"><a href="/wiki/Category:Songs" title="Category:Songs"><img src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/b/b6/ZW_Main_Page_Songs_Icon.png/revision/latest?cb=20210807235910&amp;format=original" decoding="async" loading="lazy" width="96" height="96" class="mw-file-element lazyloaded" data-image-name="ZW Main Page Songs Icon.png" data-image-key="ZW_Main_Page_Songs_Icon.png" data-relevant="0" data-src="https://static.wikia.nocookie.net/zelda_gamepedia_en/images/b/b6/ZW_Main_Page_Songs_Icon.png/revision/latest?cb=20210807235910"></a></span></div>
<div class="main-page-category-item-caption"><a href="/wiki/Category:Songs" title="Category:Songs">Songs</a></div>
</div>
</div>`

jest.setTimeout(60000); // attend jusqu'à 15 secondes si besoin

describe("check the response from openai", () => {
  it("should return a response from Openai", async () => {
    const res = await generateResponse(text); // attend bien la réponse
    expect(res).toBeDefined();
    expect(typeof res).toBe("object");
  });
});

