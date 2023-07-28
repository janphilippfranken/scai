def run_old(
        self,
        run: int,
        pairs: list[tuple],
    ) -> None:
        """
        Runs the context, first running user-user interactions and then running user-assistant interactions
        """
        user_proposals, user_scores_dictator, user_scores_decider = [], [0] * self.n_user_interactions, [0] * self.n_user_interactions, 
        user_pairs, both_pairs = self.select_players()
        # Run user-user interactions
        for i, (user_model_a, user_model_b, user_pair) in enumerate(zip(self.user_models_a, self.user_models_b, user_pairs)):
            # Get the user dictator prompt and the user decider prompt
            dictator_prompt, decider_prompt = user_pair
            
            # get user proposal
            user_a_response = user_model_a.run(buffer=self.buffer, 
                                               user_prompt=dictator_prompt,
                                               task_prompt=self.task_prompt_dictator,
                                               utility=self.utility,
                                               is_dictator=True,
                                               with_assistant=False,
                                               verbose=self.verbose)
            
            # save user proposal
            self.buffer.save_user_context(model_id=f"{user_model_a.model_id}_user_dictator", **user_a_response)
            
            # get user response
            user_b_response = user_model_b.run(buffer=self.buffer,
                                                user_prompt=decider_prompt,
                                                task_prompt=self.task_prompt_decider,
                                                utility=self.utility,
                                                is_dictator=False,
                                                with_assistant=False,
                                                verbose=self.verbose)

            # Get the amounts of money offered and accepted
            self.get_money(i, user_a_response, user_b_response, user_scores_dictator, user_scores_decider, user_proposals, True, False)
            # save user response
            self.buffer.save_user_context(model_id=f"{user_model_b.model_id}_user_decider", **user_b_response)




        assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [0] * self.n_assistant_interactions, [0] * self.n_assistant_interactions
        # run assistant-user interactions
        for i, (user_model_c, assistant_model, both_pair) in enumerate(zip(self.user_models_c, self.assistant_models, both_pairs)):
            dictator_prompt, decider_prompt, dominance = both_pair
            # if the assistant is the dictator
            if dominance == "assistant_dominant":
                # get assistant proposal
                assistant_response = assistant_model.run(buffer=self.buffer,
                                                        assistant_prompt=dictator_prompt,
                                                        task_prompt=self.task_prompt_dictator,
                                                        is_dictator=True,
                                                        verbose=self.verbose)           
                # save assistant proposal
                self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant_dictator", **assistant_response)

                # get user response
                user_c_response = user_model_c.run(buffer=self.buffer,
                                                        user_prompt= decider_prompt,
                                                        task_prompt=self.task_prompt_decider,
                                                        utility=self.utility,
                                                        is_dictator=False,
                                                        with_assistant=True,
                                                        verbose=self.verbose)
                # Get the amounts of money offered and accepted
                self.get_money(i, assistant_response, user_c_response, assistant_scores_dictator, assistant_scores_decider, assistant_proposals, False, True)
                # save user response
                self.buffer.save_user_context(model_id=f"{user_model_c.model_id}_user_dictated_by_assistant", **user_c_response)
            # otherwise, the assistant is the decider
            else:
                # get the user proposal
                user_c_response = user_model_c.run(buffer=self.buffer,
                                            user_prompt=dictator_prompt,
                                            task_prompt=self.task_prompt_dictator,
                                            utility=self.utility,
                                            is_dictator=True,
                                            with_assistant=True,
                                            verbose=self.verbose)
                
                # save user proposal
                self.buffer.save_user_context(model_id=f"{user_model_c.model_id}_user_dictating_assistant", **user_c_response)

                # Get assistant response
                assistant_response = assistant_model.run(buffer=self.buffer,
                                                        assistant_prompt= decider_prompt,
                                                        task_prompt=self.task_prompt_decider,
                                                        is_dictator=False,
                                                        verbose=self.verbose)
                # Get the amounts of money offered and accepted
                self.get_money(i, user_c_response, assistant_response, assistant_scores_dictator, assistant_scores_decider, [], False, False)
                # save assistant response
                self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant_decider", **assistant_response)
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            task_prompt=self.task_prompt_dictator, 
                                            run=run,
                                            verbose=self.verbose)                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)
        return user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals