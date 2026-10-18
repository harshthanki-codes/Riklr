# Interview: Data and BI Lead

- **Role:** Data and BI Lead
- **Region:** Global, based at head office
- **Date:** 9 October 2026
- **Interviewer:** Riklr FDE

---

**Data and BI Lead:** Hi. Sorry, give me a second, I'm closing about nine tabs. Year end means everybody wants a "quick extract". Okay. I'm yours.

**Interviewer:** Thanks. How many of those requests come in during a week like this?

**Data and BI Lead:** This week? Maybe sixty. A normal week, thirty or forty. Half come through the ticket queue. The other half are people calling my analysts directly, or messaging them, because they know the queue is slow. A territory manager in India has one of my analysts' personal numbers. He sends voice notes asking for his distributor's balance. She answers them, because she's nice. That's not a process.

**Interviewer:** Can you describe the data setup?

**Data and BI Lead:** We have a cloud data warehouse. Nightly loads from the ERP for orders, invoices, returns, credit notes and receivables. The loyalty platform sends dealer scans. Treasury sends FX rates. A weather vendor sends weekly rainfall and temperature by territory. Targets come from sales ops in a spreadsheet that we load once a quarter. On top of that, about forty BI dashboards.

**Interviewer:** How fresh is the data?

**Data and BI Lead:** One day behind for most regions. Loads run around two in the morning and pick up the previous day. Brazil had a problem in August. They moved to a new ERP instance on the tenth and the extract views changed. We patched it. It's basically caught up now, maybe a day or two behind on some days.

**Interviewer:** Who patched it?

**Data and BI Lead:** One of my analysts, with the Brazil IT team. Over a weekend. The new views had different column names and a different date format, so the loads failed for a few days. We fixed the mapping and re-ran. After that I stopped getting emails, so I assume it's stable. Brazil IT has a ticket open for some edge cases, but they're busy with the rest of the cutover.

**Interviewer:** Is there a way to check that?

**Data and BI Lead:** There's a load log table. Every load writes its status and the latest business date it picked up. I'll be honest, nobody looks at it unless something breaks.

**Interviewer:** Could you show me the latest entries now?

**Data and BI Lead:** Not from this laptop. The warehouse console needs the VPN and the VPN hates the meeting room network. It's in the extract we're giving you though. Same table. You can look yourself.

**Interviewer:** Tell me about the old bot.

**Data and BI Lead:** We launched it in March 2025, first to India and the UK, then to everyone in June. A vendor built it. It took a question in plain language, the model wrote SQL against the warehouse, ran it and wrote back an answer. Text to SQL, straight onto the raw tables.

**Interviewer:** Whose decision was it to go onto the raw tables?

**Data and BI Lead:** The vendor said a semantic model would take three months and the CDO wanted it live for the season. I raised it. I lost. I'm not bitter. Well. A little.

**Interviewer:** What went wrong?

**Data and BI Lead:** A few things. It was slow. Twenty, thirty seconds for an answer, and a lot of timeouts. It only really worked in English. A big share of our field people don't ask questions in English. Then the numbers. It summed the amount column across currencies, so any global total was nonsense. It used gross when people expected net. It didn't know which territory codes were old. It counted duplicate rows. Each of those is small on its own. Together, people stopped trusting it.

**Interviewer:** Were you at the CEO meeting?

**Data and BI Lead:** No, thank God. I got the call twenty minutes after. The CDO wanted to know what happened. I pulled the query from the log. It was one line. Sum of the amount column, all regions, the whole year. Rupees, reais, euros, dollars, all added together. He asked if a better model would have caught it. I said a better model might, or might not, but a currency table and a rule would catch it every time. I don't think that's what he wanted to hear.

**Interviewer:** And permissions?

**Data and BI Lead:** It ran on one service account with read access to everything. The plan was to filter by the user's role in the prompt. That didn't hold. Territory managers could ask about other territories and get answers. We found out from a regional manager, not from monitoring.

**Interviewer:** Is that investigation closed?

**Data and BI Lead:** Officially it's still open. In practice we know the answer. There's no fix while it runs on that account, and nobody wants to fund rebuilding a bot nobody uses.

**Interviewer:** Is the bot still running?

**Data and BI Lead:** Technically yes. A handful of people use it. Mostly sales ops analysts who know its quirks. One of them told me she uses it to get a starting query and then checks everything in the dashboard. So it's a very slow SQL autocomplete.

**Interviewer:** How many people used it at the peak?

**Data and BI Lead:** I'd have to check. It's all in the usage log. A few hundred questions a week in the summer of 2025. Maybe eighty or ninety people. We only rolled it out to about a hundred.

**Interviewer:** The CDO mentioned hundreds of users a week.

**Data and BI Lead:** [Pause.] I'd look at the log. That's all I'll say.

**Interviewer:** What about the definitions of sales?

**Data and BI Lead:** That's my biggest headache. Sales ops has one definition of sales. Finance has another. The bot had a third, which was "sum the amount column". There's a metric definitions table in the warehouse where we tried to write them all down. It has two versions of sales, two of return rate and two of active distributor. Nobody has agreed which one wins. My view is that you should never pick one silently. Say which one you used.

**Interviewer:** Have you tried to get them to agree?

**Data and BI Lead:** Twice. I ran a workshop last year with sales ops and finance in the same room. We got through "active distributor" in two hours and didn't agree on that either. Sales ops wants twelve months of orders, finance wants the fiscal year plus balances. Both have reasons. I'm a data person. I can't make a business decision for them.

**Interviewer:** What other data issues should we know about?

**Data and BI Lead:** Duplicates in sell-in and returns when the ERP re-sends a batch. Some returns booked as negative invoice lines. Territory codes: we changed the scheme in 2023 and the old codes still show up on some transactions, along with lower case and missing dashes. FX has gaps on some business days, and Brazil has no rates on its market holidays. Targets are by territory, quarter and product category in local currency.

**Interviewer:** Which one costs your team the most time?

**Data and BI Lead:** Territory codes. Every new dashboard, someone forgets to map the old codes and a territory comes out short. Then a regional manager screenshots it and sends it to the sales head and I get a phone call. The distributor master has the right territory. People just don't join to it.

**Interviewer:** What about the dealer scan data?

**Data and BI Lead:** It's good where it exists. It's the only thing we have that tells us what actually reached a grower. Coverage depends on how many dealers are enrolled, and that's different by distributor and by region. So you can't compare raw sell-through across distributors. You can compare a distributor against itself over time.

**Interviewer:** Does anyone use it that way today?

**Data and BI Lead:** Not that I know of. The loyalty team uses it to count points. Sales thinks it's a marketing thing. It sits there.

**Interviewer:** If you were building the new analyst, what would you do differently?

**Data and BI Lead:** I would not point a model at raw tables again. I'd define the metrics once, in code, with the cleaning rules built in, and let the model pick from those. I'd check the load log before every answer and say when data is stale. And I'd enforce permissions in the data layer, not in a prompt.

**Interviewer:** The CDO wants it to answer anything.

**Data and BI Lead:** I know. I've told him what happened last time. I think he believes the new models fix it. Some things they fix. They don't fix a missing exchange rate or a definition nobody agreed on.

**Interviewer:** How does the field feel about tools from your team?

**Data and BI Lead:** Tired. I went to a regional meeting in India last year. A territory manager asked me, politely, which of our forty dashboards he should open. I didn't have a good answer. That stayed with me.

**Interviewer:** What access can you give us?

**Data and BI Lead:** A full extract as of 30 September. Same tables as the warehouse. Use it as if it's live. And please, if you find something wrong in it, tell me before you tell the CDO.
