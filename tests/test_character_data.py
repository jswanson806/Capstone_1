test_appearance_data = {
            "number_of_page_results": 4,
            'results': [
                    {
                        'id': '2222',
                        'name': 'test_character',
                        'real_name': 'test_real_name',
                        'deck': 'test_deck',
                        'first_appeared_in_issue': {
                                'id': '3333',
                                'issue_number': 4444,
                                'name': 'test_first_appear',
                        },
                        'count_of_issue_appearances': 5555,
                        'image': {
                            'icon_url': 'www.testiconurl.com',
                            'original_url': 'www.testoriginalurl.com',
                        }, 
                        'publisher': {
                                'id': '6666',
                                'name': 'Test_Publisher'
                        },
                    },
                    {
                        'id': '22222',
                        'name': 'test_character1',
                        'real_name': 'test_real_name1',
                        'deck': 'test_deck1',
                        'first_appeared_in_issue': {
                                'id': '33333',
                                'issue_number': 44444,
                                'name': 'test_first_appear1',
                        },
                        'count_of_issue_appearances': 55555,
                        'image': {
                            'icon_url': 'www.testiconurl1.com',
                            'original_url': 'www.testoriginalurl1.com',
                        }, 
                        'publisher': {
                                'id': '66666',
                                'name': 'Test_Publisher1'
                        },
                    },
                    {
                        'id': '222222',
                        'name': 'test_character2',
                        'real_name': 'test_real_name2',
                        'deck': 'test_deck2',
                        'first_appeared_in_issue': {
                                'id': '333333',
                                'issue_number': 444444,
                                'name': 'test_first_appear2',
                        },
                        'count_of_issue_appearances': 555555,
                        'image': {
                            'icon_url': 'www.testiconurl2.com',
                            'original_url': 'www.testoriginalurl2.com',
                        }, 
                        'publisher': {
                                'id': '666666',
                                'name': 'Test_Publisher2'
                        },
                    },
                    {
                        'id': '2222222',
                        'name': 'test_character3',
                        'real_name': None,
                        'deck': 'test_deck3',
                        'first_appeared_in_issue': {
                                'id': '3333333',
                                'issue_number': 4444444,
                                'name': 'test_first_appear3',
                        },
                        'count_of_issue_appearances': 5555555,
                        'image': {
                            'icon_url': None,
                            'original_url': 'www.testoriginalurl3.com',
                        },  
                        'publisher': {
                                'id': None,
                                'name': None
                        },
                    }

                ]
            }

test_search_data = {
            'results': [
                    {
                        'id': '1111111111111111',
                        'name': 'test_character',
                        'real_name': None,
                    },
                    {
                        'id': '222222222222222222222',
                        'name': 'test_character',
                        'real_name': 'test_real_name',
                        'publisher': 
                            {
                                'id': '33333333333333333',
                                'name': 'Test_Publisher'
                            }
                    },
                    {
                        'id': '444444444444444444444',
                        'name': 'test_character',
                        'real_name': 'test_real_name',
                        'publisher': None 
                    }
                ]
            }

test_comic_data = {
            'results': {
                'id': '123456789',
                'name': 'testcomic'
                }
            }

test_character_data = {
            'results': {
                'id': '987654321',
                'name': 'testcharacter'
                }
            }

test_issue_credit_data = {
            'results': {
                'issue_credits': {
                    'id': '1928376450',
                    'name': 'test_appearance'
                    }
                }
            }

test_filter_appearance_data = {
                'results': {
                    'issue_credits': [
                        {
                            'id': 33333333333333,
                            'name': 'test_appearance'
                        },
                        {
                            'id': 44444444444444,
                            'name': 'test_appearance1'
                        },
                        {
                            'id': 99999999999999,
                            'name': 'Book test'
                        },
                        {
                            'id': 22222222222222,
                            'name': 'Volume test'
                        },
                        {
                            'id': 55555555555555,
                            'name': 'Volume'
                        },
                        {
                            'id': 66666666666666,
                            'name': 'HC'
                        },
                        {
                            'id': 77777777777777,
                            'name': 'TPB'
                        },
                        {
                            'id': 88888888888888,
                            'name': 'SC'
                        },
                    ]
                }
            }