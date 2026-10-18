# Interview: Global Finance Controller

- **Role:** Global Finance Controller, commercial business
- **Region:** Global, based at head office
- **Date:** 8 October 2026
- **Interviewer:** Riklr FDE

---

**Global Finance Controller:** You've caught me on day six of the year-end close. If I look at my other screen, it's not rudeness. The auditors arrive on Monday.

**Interviewer:** Understood. What does your team own in the sales numbers?

**Global Finance Controller:** The reported number. Net sales in USD, monthly. That's what goes to the board. Gross invoiced sales, minus returns, minus credit notes for schemes and rebates, converted at the monthly average rate. We also own receivables and the credit note process.

**Interviewer:** How does that differ from what sales sees?

**Global Finance Controller:** Sales looks at gross sell-in in local currency. That's what their targets are on and that's what their incentives pay on. It ignores returns and credits entirely. They also count by order date. We count by invoice date. So at every quarter end there are a few days of orders that sales counts in one quarter and we count in the next.

**Interviewer:** Which number is right?

**Global Finance Controller:** Both, for their purpose. But only one is reported externally. The issue is when someone takes a sales number and calls it revenue. Or worse, adds up the local currencies. Our global sell-in dashboard does that, I'm told. It adds rupees to dollars. India is a big share of that number in rupees, so whatever India does drives the total.

**Interviewer:** You said "I'm told". You haven't checked it yourself?

**Global Finance Controller:** I don't use the sales dashboards. My team has its own. One of my analysts opened theirs in a review last year and said, "this total can't be dollars". The BI lead confirmed it. Nobody changed it, because the sales team said they only look at their own region anyway. Except the big number at the top is what the sales head quotes.

**Interviewer:** Has that caused problems?

**Global Finance Controller:** The old bot did exactly that in front of the CEO. Global sales came back in the billions. We had a long conversation after that meeting.

**Interviewer:** Who was in that conversation?

**Global Finance Controller:** The CEO, the CDO and me. The CEO asked me one question: "Which number do I believe?" I said mine. That's the job. The CDO's view was that the model would get better. My view was that the model had added up the amount column like a junior analyst on their first day, and no model fixes that if nobody tells it what a currency is.

**Interviewer:** How do you handle currency?

**Global Finance Controller:** Treasury sends daily rates on business days. We use the monthly average of the daily rates for the month of the transaction. Weekends and holidays have no rates, so you average what's there. Note the UK bills in sterling and Canada in Canadian dollars, so it's not one currency per region.

**Interviewer:** Do sales and finance argue over specific numbers in meetings?

**Global Finance Controller:** All the time. The worst one was the Q2 review in April. The sales head said India was on track. I said it was short. We were both reading from screens, both confident. It turned out we differed on date basis, currency and credits, all three at once. It took twenty minutes with the CEO in the room. Afterwards he told both of us to put the two numbers side by side on every slide. So now we do. I'm not sure it helps. People quote the bigger one.

**Interviewer:** Tell me about returns.

**Global Finance Controller:** Normally they're one to two percent. Damaged packs, near-expiry, some unsold stock at season end. Brazil South this year was a one-off. The drought. It's a big number for that region but it doesn't change the global picture much.

**Interviewer:** Is one to two percent based on a report, or a sense of it?

**Global Finance Controller:** Our return rate is returns over gross sales in the same period, in dollars. That's our definition. Sales ops has a different one, by packs and by season. Don't ask me to reconcile the two. I've tried.

**Interviewer:** What drives the unsold stock returns in a normal year?

**Global Finance Controller:** Quarter-end loading, mostly. Sales pushes stock into distributors to hit a gross target. Some of it sells, some of it doesn't. We give the distributor return rights, so the risk comes back to us months later. I've raised it more than once. The incentive plan pays on gross, so nothing changes.

**Interviewer:** Raised it where?

**Global Finance Controller:** In the incentive committee, twice. Sales ops owns the plan. Their answer is that territory managers can't control returns or credits, so it's unfair to pay on net. I understand the argument. I also notice the people who designed the plan are paid on the same basis. That's not for your notes. Well, it's fine, put it in your notes.

**Interviewer:** And credit notes?

**Global Finance Controller:** Schemes are accrued at the end of each scheme period. The credit note should be issued within thirty days of accrual. That's the policy. Most regions are close to that.

**Interviewer:** What about India?

**Global Finance Controller:** India is slower. There's a manual validation step there. The regional team checks dealer claims before the credit is issued. It can take a bit longer. But I'd say most credits are out within a month or so.

**Interviewer:** Is there a report that shows that?

**Global Finance Controller:** The regional controller sends me a pending list every quarter. Let me see if I have the last one. Hmm. It's the June one, which is old now. I'd have to ask India for the current one. It's in a spreadsheet the regional team keeps. The ERP has the dates, but nobody runs a report on it at global level.

**Interviewer:** The territory manager we met says distributors hold back payments until credits arrive.

**Global Finance Controller:** I've heard that. Some do. It shows up as overdue receivables and then we chase. It's a dispute, not a credit risk, and we flag it as disputed in the aging report when we know about it.

**Interviewer:** How do you know about it?

**Global Finance Controller:** When the territory manager or the regional office tells us. Which is not always. Honestly, a lot of what my team learns about the field comes from collections calls. The collector rings the distributor, the distributor says "where is my credit", and that's how we find out.

**Interviewer:** How is the receivables position?

**Global Finance Controller:** Total outstanding is normal for the season. The 90-plus bucket is the one I watch. It's concentrated. A handful of distributors make up most of it. Brazil has long terms so the outstanding is large there, but that's by design.

**Interviewer:** When is the next aging snapshot?

**Global Finance Controller:** The September one runs after close, so in a week or two. The latest you'll have is the end of August.

**Interviewer:** Would an AI analyst help you?

**Global Finance Controller:** Possibly. My concern is the number. If it gives a sales manager a net sales figure that's different from mine, I spend a week reconciling. If it uses my definitions and tells people which definition it used, I'm happy. I'd rather it said "I don't know" than gave a confident wrong number.

**Interviewer:** Have you had to reconcile because of the old bot?

**Global Finance Controller:** Twice that I know of. A regional manager in Europe forwarded a bot answer to his regional controller as "the number" and asked why finance was lower. My regional controller spent two days on it. That was when I asked the BI team to stop it answering net sales questions.

**Interviewer:** What about access?

**Global Finance Controller:** Receivables are sensitive. A territory manager can see their own distributors. An agronomist should never see what a distributor owes. The old bot ran on a service account that could see everything. I signed off on it because I was told it would apply permissions. I found out later it didn't.

**Interviewer:** How did you find out?

**Global Finance Controller:** Not from a report. From a regional manager in Brazil who mentioned it in passing. That's what bothers me most. My signature is on that access request.

**Interviewer:** Anything else?

**Global Finance Controller:** The data has issues. Duplicates from ERP re-extracts. Returns sometimes booked as negative invoice lines instead of returns. Old territory codes. Treasury misses a day of rates now and then. My team cleans all that by hand at month end. Whatever you build has to deal with it too, or you'll get different numbers from mine.

**Interviewer:** By hand. In a spreadsheet?

**Global Finance Controller:** A very large spreadsheet with a lot of macros that one person on my team understands. When she's on leave, close takes two days longer. I'd love for that to be in code somewhere. Right, I need to go. The auditors want the returns reserve.
