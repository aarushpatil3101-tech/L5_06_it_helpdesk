# Reflection (draft: edit in your own words, and match the 4 questions in your handout)

1. **Which tool was most useful, and why?** Bandit found the one High issue (shell injection in `ping_user_machine`), which was the most dangerous problem in the file. Pylint found the most issues (mutable default, bare except, resource leak) and raised the score from 5.53 to 10.00. Flake8 was purely formatting.

2. **Did any tool report a false positive or something not worth fixing?** The `nosec` suppressions for B404/B603/B607 are justified: `subprocess` is needed for ping, and after the fix it uses an argument list with a validated hostname and no shell. Pylint's `too-few-public-methods` on a plain class was avoided with a dataclass rather than ignored.

3. **What did the tools miss?** Urgency was never validated (-7 accepted, `abc` crashes), `close_ticket` failed silently, and the audit trail was never used. I only found these by running the program with different inputs, so static analysis complements testing, it doesn't replace it.

4. **How would you use these tools going forward?** Run all three in a pre-commit hook and CI, fail the build on Bandit High/Medium, and keep a Pylint threshold (for example 9.5).
