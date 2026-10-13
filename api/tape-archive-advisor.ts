// Tape Archive Advisor at https://tapebackup.org/tape-archive-advisor: see api/_lib/selectionAdvisor.ts and data/advisors/tape-archive-advisor.json.
import { makeAdvisor } from "./_lib/selectionAdvisor.js";
import config from "./_advisors/tape-archive-advisor.js";

export const { POST } = makeAdvisor(config);
